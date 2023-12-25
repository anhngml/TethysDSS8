from django.http import HttpResponse
from django.shortcuts import render
from tethys_sdk.routing import controller
from tethys_sdk.gizmos import Button, MapView, MVView, MVLayer
from django.contrib import messages
from django.shortcuts import render, reverse, redirect
from .model import process_boundary_data, process_netcdf_data, load_result

@controller
def home(request):
    """
    Controller for the app home page.
    """
    data_file_error = ''
    ok_button_enable = True
    if request.POST:
        if 'boundary-extract-button' in request.POST:
            # Get Values
            has_errors = False
            ok_button_enable = False

            # Get File
            if request.FILES and 'data-file' in request.FILES:
                # Get a list of the files
                data_file = request.FILES.getlist('data-file')

            if not data_file and len(data_file) > 0:
                has_errors = True
                data_file_error = 'Data File is Required.'

            if not has_errors:
                # Process file here
                try:
                    start_datetime = request.POST['start_datetime'] if 'start_datetime' in request.POST else None
                    end_datetime = request.POST['end_datetime'] if 'end_datetime' in request.POST else None

                    success, result = process_boundary_data(data_file[0],start_datetime,end_datetime)
                    
                    if success:
                        response = HttpResponse(result, content_type='text/csv')
                        response['Content-Disposition'] = 'attachment; filename=result.csv'
                        return response
                    else:
                        messages.info(request, 'Unable to process data. Please try again.')
                        return redirect(reverse('threedidatacraft:home'))
                except:
                    messages.error(request, "Unable to process data. Please try again.")

        elif 'upload-netcdf-button' in request.POST:
            has_errors = False
            # Get File
            if request.FILES and 'data-file' in request.FILES:
                # Get a list of the files
                data_file = request.FILES.getlist('data-file')

            if not data_file and len(data_file) > 0:
                has_errors = True
                data_file_error = 'Data File is Required.'

            if not has_errors:
                process_netcdf_data(data_file[0])
                # Process file here

                pass

    stations = []
    features = []
    lat_list = []
    lng_list = []

    stations = load_result()

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
                'waterlevel': station.waterlevel
            }
        }
        features.append(station_feature)

    # Define GeoJSON FeatureCollection
    stations_feature_collection = {
        'type': 'FeatureCollection',
        'crs': {
            'type': 'name',
            'properties': {
                'name': 'EPSG:32648'
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

    # Define view centered on dam locations
    try:
        view_center = [sum(lng_list) / float(len(lng_list)), sum(lat_list) / float(len(lat_list))]
    except ZeroDivisionError:
        view_center = [105.772204, 10.034976]

    # Create a Map View Layer
    stations_layer = MVLayer(
        source='GeoJSON',
        options=stations_feature_collection,
        legend_title='Stations',
        layer_options={'style': style},
        feature_selection=True
    )

    view_options = MVView(
        projection='EPSG:32648',
        # projection='EPSG:4326',
        center=view_center,
        zoom=8,
        maxZoom=18,
        minZoom=2
    )

    wqi_map = MapView(
        height='100%',
        width='100%',
        layers=[stations_layer],
        view=view_options,
        # basemap=['OpenStreetMap'],
        basemap=[{'XYZ': {'url': 'https://maps.becagis.vn/tiles/basemap/light/{z}/{x}/{y}.png', 'control_label': 'becagis'}}]
        # https://maps.becagis.vn/tiles/basemap/light/{z}/{x}/{y}.png
    )

    boundary_extract_button = Button(
        display_text='Xử lý',
        name='boundary-extract-button',
        # icon='plus-square',
        style='btn btn-primary',
        disabled= not ok_button_enable,
        attributes={'form': 'boundary-data-form'},
        submit=True
    )

    upload_netcdf_button = Button(
        display_text='Tải lên',
        name='upload-netcdf-button',
        # icon='plus-square',
        style='btn btn-primary',
        disabled= not ok_button_enable,
        attributes={'form': 'upload-netcdf-data-form'},
        submit=True
    )

    cancel_button = Button(
        display_text='Cancel',
        name='cancel-button',
        href=reverse('threedidatacraft:home')
    )

    context = {
        'wqi_map': wqi_map,
        'boundary_extract_button': boundary_extract_button,
        'upload_netcdf_button': upload_netcdf_button,
        'cancel_button': cancel_button,
        'data_file_error': data_file_error,
    }

    return render(request, 'threedidatacraft/home.html', context)