from tethys_sdk.routing import controller
from tethys_sdk.gizmos import Button, MapView, MVView, DataTableView,MVLayer
from django.utils.html import format_html
from django.contrib import messages
from django.shortcuts import render, reverse, redirect
from .model import Station, add_new_station, get_all_stations, assign_hydrograph_to_station, get_hydrograph
from .app import WaterLevel as app
from .helpers import create_hydrograph
from minio import Minio
from minio.error import S3Error
from .model import Hydrograph, HydrographPoint
import pandas as pd
from django.http import HttpResponseNotAllowed, JsonResponse
import requests
import string
import re
import json

def sanitize_string(input_string):
    # Chỉ giữ lại chữ cái thường, số, - và _
    sanitized_string = re.sub(r'[^a-z0-9\-_]', '', input_string)
    return sanitized_string

@controller
def home(request):
    """
    Controller for the app home page.
    """
    # Get list of dams and create dams MVLayer:
    stations = get_all_stations()
    features = []
    lat_list = []
    lng_list = []

    for station in stations:
        if station.latitude is None or station.longitude is None:
            continue
        lat_list.append(station.latitude)
        lng_list.append(station.longitude)

        station_feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [station.longitude, station.latitude],

            },
            'properties': {
                'id': station.id,
                'name': station.name,
            }
        }
        features.append(station_feature)

    # Define GeoJSON FeatureCollection
    stations_feature_collection = {
        'type': 'FeatureCollection',
        'crs': {
            'type': 'name',
            'properties': {
                'name': 'EPSG:4326'
            }
        },
        'features': features
    }

    style = {'ol.style.Style': {
        'image': {'ol.style.Circle': {
            'radius': 10,
            'fill': {'ol.style.Fill': {
                'color':  '#d84e1f'
            }},
            'stroke': {'ol.style.Stroke': {
                'color': '#ffffff',
                'width': 1
            }}
        }}
    }}

    # Create a Map View Layer
    stations_layer = MVLayer(
        source='GeoJSON',
        options=stations_feature_collection,
        legend_title='Stations',
        layer_options={'style': style},
        feature_selection=True
    )

    # Define view centered on dam locations
    try:
        view_center = [sum(lng_list) / float(len(lng_list)), sum(lat_list) / float(len(lat_list))]
    except ZeroDivisionError:
        view_center = [105.772204, 10.034976]

    # Define view options
    view_options = MVView(
        projection='EPSG:4326',
        center=view_center,
        zoom=8,
        maxZoom=18,
        minZoom=2
    )

    background_map = MapView(
        height='100%',
        width='100%',
        layers=[stations_layer],
        view=view_options,
        basemap=[{'XYZ': {'url': 'https://maps.becagis.vn/tiles/basemap/light/{z}/{x}/{y}.png', 'control_label': 'becagis'}}]
        # basemap=['OpenStreetMap'],
    )

    context = {
        # 'save_button': save_button,
        # 'edit_button': edit_button,
        # 'remove_button': remove_button,
        # 'previous_button': previous_button,
        # 'next_button': next_button,
        'background_map': background_map
    }

    return render(request, 'water_level/home.html', context)

@controller(name='stations', url='stations')
def list_stations(request):
    stations = get_all_stations()
    table_rows = []

    for station in stations:
        hydrograph_id = get_hydrograph(station.id)
        if hydrograph_id:
            url = reverse('water_level:hydrograph', kwargs={'hydrograph_id': hydrograph_id})
            station_hydrograph = format_html('<a class="btn btn-primary" href="{}">Hydrograph Plot</a>'.format(url))
        else:
            station_hydrograph = format_html('<a class="btn btn-primary disabled" title="No hydrograph assigned" '
                                         'style="pointer-events: auto;">Hydrograph Plot</a>')

        table_rows.append(
            (
                station.uuid, station.name,
                station_hydrograph
            )
        )

    stations_table = DataTableView(
        column_names=('Code', 'Name', 'Hydrograph'),
        rows=table_rows,
        searching=False,
        orderClasses=False,
        lengthMenu=[[10, 25, 50, -1], [10, 25, 50, "All"]],
    )
    context = {
        "stations_table": stations_table
    }
    return render(request, 'water_level/list_stations.html', context)

@controller(url='stations/add')
def add_station(request):
    context = {

    }
    return render(request, 'water_level/add_station.html', context)

@controller(url='hydrographs/{hydrograph_id}')
def hydrograph(request, hydrograph_id):
    """
    Controller for the Hydrograph Page.
    """
    hydrograph_plot = create_hydrograph(hydrograph_id)

    context = {
        'hydrograph_plot': hydrograph_plot
    }
    return render(request, 'water_level/hydrograph.html', context)

@controller(url='hydrographs/{station_id}/ajax')
def hydrograph_ajax(request, station_id):
    """
    Controller for the Hydrograph Page.
    """
    # Get stations from database
    Session = app.get_persistent_store_database('primary_db_v2', as_sessionmaker=True)
    session = Session()
    station = session.query(Station).get(int(station_id))

    if station.hydrograph:
        hydrograph_plot = create_hydrograph(station.hydrograph.id, height='250px')
    else:
        hydrograph_plot = None

    context = {
        'hydrograph_plot': hydrograph_plot,
    }

    session.close()
    return render(request, 'water_level/hydrograph_ajax.html', context)
## Doan put csv to minio
@controller(url='export_result/{station_id}')
def export_result(request, station_id):
    """
    """
    messages.info(request, 'Processing ...')
    # Get stations from database
    Session = app.get_persistent_store_database('primary_db_v2', as_sessionmaker=True)
    session = Session()
    station = session.query(Station).get(int(station_id))

    json_response = {'success': False}
    link_url = ''
    if station.hydrograph:
        try:
            hydrograph = session.query(Hydrograph).get(int(station.hydrograph.id))
            points = hydrograph.points #.order_by(desc(HydrographPoint.time))
            points_count = len(points)
            points = points if points_count <= 20 else points[-20:-1]
    
            time = []
            level = []
            level_pred = []

            for hydro_point in points:
                time.append(hydro_point.time)
                level.append(hydro_point.level)
                level_pred.append(hydro_point.level_pred)
            df = pd.DataFrame({"time":time,"level":level,"level_pred":level_pred })
            df.to_csv(str(station.name)+'_'+'water_level'+'.csv', index=False) 

            client = Minio(
            "storage.mkdc.vn",
            access_key="YvaFGyxc4UYfG9er",
            secret_key="eoAiwmabGvTgn9Jts7htdrfP49UPpELq",
            )
            a = client.fput_object(
                "data2product", str(station.name)+'_'+'water_level'+'.csv', str(station.name)+'_'+'water_level'+'.csv',
            )
            # response =  client.get_object(bucket_name=a.bucket_name,object_name=a.object_name)
            path_url = "https://storage.mkdc.vn/"+"data2product/"+ str(station.name)+'_'+'water_level'+'.csv', str(station.name)+'_'+'water_level'+'.csv'

            url = "https://opendata.mkdc.com.vn/api/3/action/package_create"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJ4VDktX3hlR1lxY2lMbUszaWtENzd3SVZTUzBYdjJtMnV4c1k3b3J4aDdjIiwiaWF0IjoxNzAyNjU1MjA4fQ.YWi2VGUl0IuS2ByjX1sZwEG46w0BUTnC1oKfAhdHqmY'
            }
            request_body = {
                "name": sanitize_string(str(a.object_name)),
                "title": str(a.object_name),
                "notes": "CSV Describe",
                "owner_org": "39f7a753-904d-4d1d-9fcc-583382720332",
                "tags": [{"name": "csv"}],
                "extras": [
                    {
                        "key": "mkdc_portal_display",
                        "value": "true"
                    }
                ],
                "resources": [
                    {
                        "url": path_url,
                        "format": "csv",
                        "name": sanitize_string(str(a.object_name)),
                        "hash": "e0d123e5f316bef78bfdf5a008837577",
                        "size": "1024",
                        "last_modified": "2023-08-16T08:50:11.141400",
                        "created": "2023-08-16T08:50:11.141400"
                    }
                ]
            }
            response = requests.post(url, headers=headers, json=request_body)

            # # Kiểm tra trạng thái và in ra kết quả
            # if response.status_code == 200:
            #     print("Request thành công!")
            #     print("Response:")
            #     print(response.json())
            # else:
            #     print(f"Request thất bại với mã lỗi {response.status_code}")
            #     print("Response:")
            #     print(response.text)



            json_response.update({
                'success': True
            })
        except Exception as e:
            print(str(e))
            json_response['error'] = f'An unexpected error has occurred. Please try again.'
            json_response['data'] = str(e)

    session.close()
    return JsonResponse(json_response)