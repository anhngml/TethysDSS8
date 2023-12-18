from tethys_sdk.routing import controller
from tethys_sdk.gizmos import Button, MapView, MVView, DataTableView,MVLayer
from django.utils.html import format_html
from django.contrib import messages
from django.shortcuts import render, reverse, redirect
from .model import Station, add_new_station, get_all_stations, assign_hydrograph_to_station, get_hydrograph
from .app import WaterLevel as app
from .helpers import create_hydrograph

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
        basemap=['OpenStreetMap'],
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