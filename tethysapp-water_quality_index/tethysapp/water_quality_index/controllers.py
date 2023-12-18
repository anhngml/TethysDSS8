from django.shortcuts import render
from tethys_sdk.routing import controller
from tethys_sdk.gizmos import Button, MapView, MVView, MVLayer
from django.contrib import messages
from django.shortcuts import render, reverse, redirect
from .model import process_data, load_result

@controller
def home(request):
    """
    Controller for the app home page.
    """
    data_file_error = ''
    ok_button_enable = True
    if request.POST and 'ok-button' in request.POST:
        # Get Values
        has_errors = False

        # Get File
        if request.FILES and 'data-file' in request.FILES:
            # Get a list of the files
            data_file = request.FILES.getlist('data-file')

        if not data_file and len(data_file) > 0:
            has_errors = True
            data_file_error = 'Data File is Required.'

        if not has_errors:
            # Process file here
            ok_button_enable = False
            success = process_data(data_file[0])
            ok_button_enable = True
            # Provide feedback to user
            if success:
                messages.info(request, 'Successfully.')
            else:
                messages.info(request, 'Unable to process data. Please try again.')
            return redirect(reverse('water_quality_index:home'))

        messages.error(request, "Please fix errors.")

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
                'name': station.id,
                'WQI_I': station.WQI_I,
                'WQI_II': station.WQI_II,
                'WQI_III': station.WQI_III,
                'WQI_IV': station.WQI_IV,
                'WQI_V': station.WQI_V,
                'WQI': station.WQI,
                'WQI_Level': station.WQI_Level,
                'WQI_Color': station.WQI_Color,
                # WQI_I,WQI_II,WQI_III,WQI_IV,WQI_V,WQI
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
        projection='EPSG:4326',
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
        basemap=[{'XYZ': {'url': 'https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png', 'control_label': 'Wikimedia'}}]
        # https://maps.becagis.vn/tiles/basemap/light/{z}/{x}/{y}.png
    )

    ok_button = Button(
        display_text='Upload',
        name='ok-button',
        # icon='plus-square',
        style='btn btn-primary',
        disabled= not ok_button_enable,
        attributes={'form': 'add-data-form'},
        submit=True
    )

    cancel_button = Button(
        display_text='Cancel',
        name='cancel-button',
        href=reverse('water_quality_index:home')
    )

    context = {
        'wqi_map': wqi_map,
        'ok_button': ok_button,
        'cancel_button': cancel_button,
        'data_file_error': data_file_error,
    }

    return render(request, 'water_quality_index/home.html', context)