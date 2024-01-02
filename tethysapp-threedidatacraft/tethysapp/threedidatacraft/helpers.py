from plotly import graph_objs as go
from tethys_gizmos.gizmo_options import PlotlyView

from sqlalchemy import asc, desc
from datetime import datetime
import numpy as np
from tethys_sdk.gizmos import TimeSeries
from .model import load_result
from sklearn.metrics import r2_score


def create_plot(station, height='520px', width='100%'):
    """
    Generates a plotly view of a hydrograph.
    """
    level = station.waterlevel.replace('[', '').replace(']', '').split(',')
    level = list(map(lambda x: float(x), level))
    level = np.array(level)
    # level[:] = 1
    level[level == -9999.0] = None
    time = station.time.replace('[', '').replace(']', '').split(',')
    time = list(map(lambda x: datetime.fromtimestamp(int(x)), time))
    obs_time = station.obs_time
    obs_level = station.obs_value

    if obs_time is not None and obs_level is not None:
        obs_time = list(map(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'), obs_time))
        # print(type(obs_time[0]))
        uni_time = list(set(time).intersection(set(obs_time)))
        # print(uni_time)
        if len(uni_time) > 0:
            min_time = min(uni_time)
            max_time = max(uni_time)

            sim_level_sel = level[time.index(min_time): time.index(max_time)]
            obs_level_sel = obs_level[obs_time.index(min_time): obs_time.index(max_time)]
            # print(sim_level_sel, obs_level_sel)
            rmse = np.linalg.norm(sim_level_sel - obs_level_sel) / np.sqrt(len(obs_level_sel))
            coefficient_of_dermination = r2_score(obs_level_sel, sim_level_sel)

    hydrograph_go = go.Scatter(
        x=time,
        y=level,
        name='sim',
        line={'color': '#0080ff', 'width': 1, 'shape': 'spline'},
    )
    hydrograph_pred_go = go.Scatter(
        x=obs_time,
        y=obs_level,
        name='obs',
        line={'color': 'red', 'width': 1, 'shape': 'spline'},
    )
    data = [hydrograph_go, hydrograph_pred_go]
    layout = {
        'title': 'Benchmark for {0}: RMSE={1}; R2={2}'.format(station.id, round(rmse, 2), round(coefficient_of_dermination, 2)) \
        if station.obs_time is not None else '',
        'xaxis': {'title': 'Time (hr)'},
        'yaxis': {'title': 'Level (cm)'},
    }
    figure = {'data': data, 'layout': layout}
    variables_plot = PlotlyView(figure, height=height, width=width)


    timeseries_plot = TimeSeries(
        height='500px',
        width='500px',
        engine='highcharts',
        title='Irregular Timeseries Plot',
        y_axis_title='Snow depth',
        y_axis_units='m',
        series=[{
            'name': 'Winter 2007-2008',
            'data': [
                [datetime(2008, 12, 2), 0.8],
                [datetime(2008, 12, 9), 0.6],
                [datetime(2008, 12, 16), 0.6],
                [datetime(2008, 12, 28), 0.67],
                [datetime(2009, 1, 1), 0.81],
                [datetime(2009, 1, 8), 0.78],
                [datetime(2009, 1, 12), 0.98],
                [datetime(2009, 1, 27), 1.84],
                [datetime(2009, 2, 10), 1.80],
                [datetime(2009, 2, 18), 1.80],
                [datetime(2009, 2, 24), 1.92],
                [datetime(2009, 3, 4), 2.49],
                [datetime(2009, 3, 11), 2.79],
                [datetime(2009, 3, 15), 2.73],
                [datetime(2009, 3, 25), 2.61],
                [datetime(2009, 4, 2), 2.76],
                [datetime(2009, 4, 6), 2.82],
                [datetime(2009, 4, 13), 2.8],
                [datetime(2009, 5, 3), 2.1],
                [datetime(2009, 5, 26), 1.1],
                [datetime(2009, 6, 9), 0.25],
                [datetime(2009, 6, 12), 0]
            ]
        }]
    )
    # return timeseries_plot
    return variables_plot

def create_benchmark(point_id):
    try:
        print(point_id)
        stations = load_result()
        station = next(x for x in stations if x.id == int(point_id))
        return create_plot(station=station)
    except Exception as e:
        print('====')
        print(str(e))
        pass