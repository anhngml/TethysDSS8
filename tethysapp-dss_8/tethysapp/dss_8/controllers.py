from datetime import datetime
from django.shortcuts import render
from tethys_sdk.routing import controller
from tethys_sdk.gizmos import MapView, MVView, Button
from tethys_sdk.gizmos import TimeSeries

@controller
def home(request):
    """
    Controller for the app home page.   
    """
    selected_point_code = request.GET['tram'] if 'tram' in request.GET else ''
    print(selected_point_code)
    monitoring_points = [{'code': 'an_thuan', 'name': 'An Thuận'}, {'code': 'binh_dai', 'name': 'Bình Đại'}, {'code': 'ganh_hao', 'name': 'Gành Hào'}]
    
    selected_point = None

    for p in monitoring_points:
        if p['code'] == selected_point_code:
            selected_point = p
            break

    # Define view options
    view_options = MVView(
        projection='EPSG:4326',
        center=[105.772204, 10.034976],
        zoom=12,
        maxZoom=18,
        minZoom=2
    )

    timeseries_plot = TimeSeries(
    height='500px',
    width='800px',
    engine='highcharts',
    title='Biểu đồ mực nước tại trạm ' + selected_point['name'],
    y_axis_title='Snow depth',
    y_axis_units='m',
    series=[{
        'name': '2022-2023',
        'data': [
            [datetime(2022, 12, 2), 0.8],
            [datetime(2022, 12, 9), 0.6],
            [datetime(2022, 12, 16), 0.6],
            [datetime(2022, 12, 28), 0.67],
            [datetime(2023, 1, 1), 0.81],
            [datetime(2023, 1, 8), 0.78],
            [datetime(2023, 1, 12), 0.98],
            [datetime(2023, 1, 27), 1.84],
            [datetime(2023, 2, 10), 1.80],
            [datetime(2023, 2, 18), 1.80],
            [datetime(2023, 2, 24), 1.92],
            [datetime(2023, 3, 4), 2.49],
            [datetime(2023, 3, 11), 2.79],
            [datetime(2023, 3, 15), 2.73],
            [datetime(2023, 3, 25), 2.61],
            [datetime(2023, 4, 2), 2.76],
            [datetime(2023, 4, 6), 2.82],
            [datetime(2023, 4, 13), 2.8],
            [datetime(2023, 5, 3), 2.1],
            [datetime(2023, 5, 26), 1.1],
            [datetime(2023, 6, 9), 0.25],
            [datetime(2023, 6, 12), 0]
        ]
    }]
) if selected_point is not None else None

    dss8_map = MapView(
        height='100%',
        width='100%',
        layers=[],
        view=view_options,
        basemap=['OpenStreetMap'],
    )


    add_dam_button = Button(
        display_text='Add...',
        name='add-dam-button',
        icon='plus-square',
        style='success'
    )

    context = {
        'dss8_map': dss8_map,
        'add_dam_button': add_dam_button,
        'monitoring_points': monitoring_points,
        'selected_point': selected_point,
        'timeseries_plot': timeseries_plot,
    }

    return render(request, 'dss_8/home.html', context)