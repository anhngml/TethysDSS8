import pandas as pd
from .dss1 import dss1_final
from django.core.files.storage import FileSystemStorage
import os.path
from .app import Threedidatacraft as app
from datetime import datetime
import numpy as np
import netCDF4 as nc
from netCDF4 import Dataset
import netCDF4
from pyproj import Proj, transform
import cftime
from scipy.interpolate import interp1d

def process_boundary_data(data_file,start_datetime=None,end_datetime=None):
  
  start_datetime = datetime.strptime(start_datetime, '%Y-%m-%dT%H:%M').replace(minute=0, second=0, microsecond=0) if start_datetime is not None else None
  end_datetime = datetime.strptime(end_datetime, '%Y-%m-%dT%H:%M').replace(minute=0, second=0, microsecond=0) if end_datetime is not None else None

  points_sheet_name = app.get_custom_setting(name="points_sheet")
  boundary_type_map = app.get_custom_setting(name="boundary_type_map")
  sequence_sheets_list = [i for i in map(lambda x:x["sheet_name"],boundary_type_map.values())]
  sequence_sheets_list.append(points_sheet_name)

  xls = pd.ExcelFile(data_file)
  points = pd.read_excel(xls, points_sheet_name)

  points = points[['id', 'boundary_type', 'Station']]
  result = pd.DataFrame({"id":points['id']})
  
  timeseries = []

  metric_sheets = {}


  for index, row in points.iterrows():
    boundary_map = boundary_type_map[str(row['boundary_type'])]
    station_name_row = boundary_map["station_name_row"]-2
    first_data_row_conf = boundary_map["first_data_row"]-2
    time_column = boundary_map["time_column"]-1
    # metric_sheet = pd.read_excel(xls, boundary_map["sheet_name"], parse_dates=[time_column], 
    #                              date_format=app.get_custom_setting("datetime_format"))
    sheet_name = boundary_map['sheet_name']
    metric_sheet =  pd.read_excel(xls, boundary_map["sheet_name"]) if sheet_name not in metric_sheets else metric_sheets[sheet_name]
    metric_sheets[sheet_name] = metric_sheet

    station_name = str(row["Station"]).upper()
    if True:
      times = metric_sheet.iloc[first_data_row_conf:,time_column].tolist()
      if isinstance(times[0], str):
        times = list(map(lambda x:datetime.strptime(x, app.get_custom_setting(name="datetime_format")),times))
      
      np_times = np.array(times)

    first_data_row = np.argmax(np_times >= start_datetime) + first_data_row_conf if start_datetime is not None else first_data_row_conf
    last_data_row = np.argmax(np_times > end_datetime) + first_data_row_conf if end_datetime is not None else -1

    station_array =\
    metric_sheet.iloc[[station_name_row]].values.flatten().tolist() if station_name_row >= 0 \
    else list(metric_sheet.columns)

    station_array = list(map(lambda x:str(x).upper(),station_array))
    series_col = station_array.index(station_name) if station_name in station_array else -1

    series = metric_sheet.iloc[first_data_row: last_data_row,series_col].tolist() if series_col>= 0 else []
    # doan
    
    x = []
    # x.append(0)
    for i in range(len(series)):
      tmp = int((times[first_data_row+i-2]-start_datetime).total_seconds())
      x.append(tmp)
    if len(series) == 0:
      timeseries.append([])
      continue
    
    
    tmp = int((end_datetime-start_datetime).total_seconds())
    step = 3600 

    x_interp = np.linspace(0, tmp, int(tmp/step)+1)
    y = np.full(int(tmp/step), None)
    # y = np.array(y)

    tt = 0
    kt = 0
    for i in range(len(x_interp)-1):
      if x_interp[i] in x and not np.isnan(series[tt]):
        # print("series[tt]",series[tt])
        y[i] = series[tt]
        tt += 1
        kt = 1
    if kt  == 0 :
      timeseries.append([])
      continue

    # print(y)
    # Find non-missing indices
    non_nan_indices = np.where(np.array(y) != None)[0]

    # Create an interpolation function
    interp_func = interp1d([x_interp[i] for i in non_nan_indices], 
                          [y[i] for i in non_nan_indices], 
                          kind='linear', fill_value="extrapolate")

    
    y_interp = [val if val is not None else '{:.4f}'.format(float(interp_func(x_interp[i]))) for i, val in enumerate(y)]
   
    series_ = []
    for i in range(len(y_interp)):
      series_.append(str(int(x_interp[i]))+','+str(y_interp[i]))
    #
    series = "\n".join(map(lambda x:str(x),series_))

    timeseries.append(series)
  
  result["timeseries"]= timeseries
  return True, result.to_csv(index=False)

def process_netcdf_data(data_file):
  data_folder = app.get_custom_setting(name="data_folder")
  saved_file = FileSystemStorage(location=data_folder).save(data_file.name, data_file)
  saved_file = FileSystemStorage(location=data_folder).path(saved_file)
  ds = nc.Dataset(saved_file)
  
  xcc2d = ds["Mesh2DFace_xcc"][:]
  ycc2d = ds["Mesh2DFace_ycc"][:]
  s2d = ds["Mesh2D_s1"][:]
  time = ds["time"][:]
  units = ds.variables['time'].units
  calendar = 'standard'
  # times32 = netCDF4.num2date(time, units=units, calendar=calendar)
  times32 = cftime.num2pydate(time, units=units, calendar=calendar)
  times32 = list(map(lambda x: int(x.timestamp()), times32))

  df = pd.DataFrame(data={ 'id': range(0, len(xcc2d)), 'x': xcc2d, 'y': ycc2d, 'time': np.zeros((len(xcc2d), len(times32))).tolist(), 'WaterLevel': s2d.transpose().tolist() })
  crs_init = Proj('epsg:32648')
  crs_wgs84 = Proj('epsg:4326')
  for index, row in df.iterrows():
    x, y = row['x'], row['y']
    lat, lon = transform(crs_init, crs_wgs84, x, y)
    df.at[index, 'x'] = lat
    df.at[index, 'y'] = lon
    df.at[index, 'time'] = times32

  df.to_csv(data_folder+'/result.csv', index=False)

def process_obs_file(data_file, start_datetime, end_datetime, point_id):
  data_folder = app.get_custom_setting(name="data_folder")
  df = pd.read_csv(data_file)
  
  start_datetime = datetime.strptime(start_datetime, '%Y-%m-%dT%H:%M') if start_datetime is not None else None
  end_datetime = datetime.strptime(end_datetime, '%Y-%m-%dT%H:%M') if end_datetime is not None else None

  times = df.iloc[:,0].tolist()
  if isinstance(times[0], str):
    times = list(map(lambda x:datetime.strptime(x, app.get_custom_setting(name="datetime_format")),times))
  
  np_times = np.array(times)

  print(start_datetime.month, end_datetime.month, np_times[0].month)

  first_data_row = np.argmax(np_times >= start_datetime) if start_datetime is not None else 0
  last_data_row = np.argmax(np_times > end_datetime) if end_datetime is not None else -1

  times = times[first_data_row:last_data_row]
  series = df.iloc[first_data_row: last_data_row, 1].tolist()
  df = pd.DataFrame({ 'time': times, 'value': series })
  df.to_csv(f'{data_folder}/obs_{point_id}.csv', index=False)

def load_result():
  stations = []
  data_folder = app.get_custom_setting(name="data_folder")
  result_file = data_folder+'/result.csv'
  # crs_init = Proj('epsg:32648')
  # crs_wgs84 = Proj('epsg:4326')
  try:
    if os.path.isfile(result_file):
      df = pd.read_csv(result_file,skiprows=[1])
      for index, row in df.iterrows():
        station = lambda: None
        station.id = row['id']
        obs_file = f'{data_folder}/obs_{station.id}.csv'
        if os.path.isfile(obs_file):
          df = pd.read_csv(obs_file)
          station.obs_time = df.iloc[:, 0].tolist()
          station.obs_value = df.iloc[:, 1].tolist()
        else:
          station.obs_time = None
          station.obs_value = None

        x, y = row['x'], row['y']
        # lat, lon = transform(crs_init, crs_wgs84, x, y)
        station.latitude = x # round(lat, 6)
        station.longitude = y # round(lon, 6)
        station.time = row['time']
        station.waterlevel = row['WaterLevel']
        
        stations.append(station)
  except:
    print('====')
  return stations