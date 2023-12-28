from django.http import HttpResponse
from django.shortcuts import render
from tethys_sdk.routing import controller
from tethys_sdk.gizmos import Button, MapView, MVView, MVLayer, DatePicker
from django.contrib import messages
from django.shortcuts import render, reverse, redirect
from .helpers import create_plot, create_benchmark

from .model import process_boundary_data, process_netcdf_data, load_result, process_obs_file

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

    # stations = []
    features = []
    lat_list = []
    lng_list = []
    stations = load_result()

    for station in stations:
        # print(station.latitude, station.longitude)
        if station.latitude is None or station.longitude is None:
            continue
        lat_list.append(station.latitude)
        lng_list.append(station.longitude)

        station_feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                # 'coordinates': [station.latitude, station.longitude],
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
                # 'name': 'EPSG:4326'
                'name': 'EPSG:4326'
            }
        },
        'features': features
    }

    style = {'ol.style.Style': {
        'image': {'ol.style.Circle': {
            'radius': 3,
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
        # projection='epsg:4326',
        # projection='EPSG:4326',
        center=view_center,
        zoom=14,
        maxZoom=28,
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

@controller(url='benchmark/{point_id}/obs')
def upload_obs(request, point_id):
    """
    Controller for the Add Dam page.
    """
    # Default Values
    from_datetime = request.POST['from_datetime'] if 'from_datetime' in request.POST else None
    to_datetime = request.POST['to_datetime'] if 'to_datetime' in request.POST else None
    hydrograph_file = None
    # Errors
    from_datetime_error = ''
    to_datetime_error = ''
    hydrograph_file_error = ''

    # Handle form submission
    if request.POST and 'upload-button' in request.POST:
        # Get values
        has_errors = False
        from_datetime = request.POST.get('from_datetime', None)
        to_datetime = request.POST.get('to_datetime', None)
        # Get File
        if request.FILES and 'sequence-file' in request.FILES:
            # Get a list of the files
            hydrograph_file = request.FILES.getlist('sequence-file')

        if not hydrograph_file and len(hydrograph_file) > 0:
            has_errors = True
            hydrograph_file_error = 'Hydrograph File is Required.'

        # Validate
        # if not from_datetime:
        #     has_errors = True
        #     from_datetime_error = 'From date is required.'

        # if not to_datetime:
        #     has_errors = True
        #     to_datetime_error = 'To date is required.'

        if not has_errors:
            process_obs_file(hydrograph_file[0], from_datetime, to_datetime, point_id)
            return redirect(f'/apps/threedidatacraft/benchmark/{point_id}')

        messages.error(request, "Please fix errors.")

    upload_button = Button(
        display_text='Upload',
        name='upload-button',
        icon='plus-square',
        style='success',
        attributes={'form': 'upload-obs-form'},
        submit=True
    )

    cancel_button = Button(
        display_text='Cancel',
        name='cancel-button',
        href='/apps/threedidatacraft/benchmark/'+point_id
    )

    context = {
        # 'from_datetime_input': from_datetime_input,
        # 'to_datetime_input': to_datetime_input,
        'hydrograph_file_error': hydrograph_file_error,
        'upload_button': upload_button,
        'cancel_button': cancel_button,
    }

    return render(request, 'threedidatacraft/upload_obs.html', context)

@controller(url='benchmark/{point_id}')
def benchmark(request, point_id):
    benchmark_plot = create_benchmark(point_id)

    upload_obs_button = Button(
        display_text='Upload obs',
        name='upload-obs-button',
        icon='plus-square',
        style='success',
        href='obs'
    )

    context = {
        'benchmark_plot': benchmark_plot,
        'upload_obs_button': upload_obs_button
    }
    return render(request, 'threedidatacraft/benchmark.html', context)

@controller(url='plot/{station_id}/ajax')
def plot_ajax(request, station_id):
    """
    Controller for the Hydrograph Page.
    """
    stations = load_result()
    station = None
    # Get stations from database
    for x in stations:
        if x.id == int(station_id):
            # print("i found it!")
            station = x
            break
    else:
        station = None

    if station and station.waterlevel:
        variables_plot = create_plot(station, height='250px')
    else:
        variables_plot = None

    context = {
        'variables_plot': variables_plot,
    }
    return render(request, 'threedidatacraft/plot_ajax.html', context)