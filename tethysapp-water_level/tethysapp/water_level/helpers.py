from plotly import graph_objs as go
from tethys_gizmos.gizmo_options import PlotlyView

from .app import WaterLevel as app
from .model import Hydrograph, HydrographPoint

from sqlalchemy import asc, desc


def create_hydrograph(hydrograph_id, height='520px', width='100%'):
    """
    Generates a plotly view of a hydrograph.
    """
    # Get objects from database
    Session = app.get_persistent_store_database('primary_db_v2', as_sessionmaker=True)
    session = Session()
    hydrograph = session.query(Hydrograph).get(int(hydrograph_id))
    station = hydrograph.station
    time = []
    level = []
    level_pred = []

    points = hydrograph.points #.order_by(desc(HydrographPoint.time))
    last_point = points[-1]

    for hydro_point in points:
        time.append(hydro_point.time)
        level.append(hydro_point.level)

    future_time = last_point.time
    level_pred = list(map(lambda x: None, level))
    level_pred.append(last_point.level)
    level_pred.extend(last_point.level_pred)

    for pred in level_pred:
        time.append(future_time)
        future_time += 1
    # level_pred = level
    # Build up Plotly plot
    hydrograph_go = go.Scatter(
        x=time,
        y=level,
        name='level',
        line={'color': '#0080ff', 'width': 5, 'shape': 'spline'},
    )
    hydrograph_pred_go = go.Scatter(
        x=time,
        y=level_pred,
        name='pred',
        line={'color': 'red', 'width': 5, 'shape': 'spline'},
    )
    data = [hydrograph_go, hydrograph_pred_go]
    layout = {
        # 'title': 'Hydrograph for {0}'.format(station.name),
        'xaxis': {'title': 'Time (hr)'},
        'yaxis': {'title': 'Level (cm)'},
    }
    figure = {'data': data, 'layout': layout}
    hydrograph_plot = PlotlyView(figure, height=height, width=width)
    session.close()
    return hydrograph_plot
