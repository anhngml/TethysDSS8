import pandas as pd
from .dss1 import dss1_final
from django.core.files.storage import FileSystemStorage
import os.path
from .app import Threedidatacraft as app
from datetime import datetime
import numpy as np

def process_data(data_file,start_datetime=None,end_datetime=None):
  
  start_datetime = datetime.strptime(start_datetime, '%Y-%m-%dT%H:%M') if start_datetime is not None else None
  end_datetime = datetime.strptime(end_datetime, '%Y-%m-%dT%H:%M') if end_datetime is not None else None

  points_sheet_name = app.get_custom_setting(name="points_sheet")
  boundary_type_map = app.get_custom_setting(name="boundary_type_map")
  sequence_sheets_list = [i for i in map(lambda x:x["sheet_name"],boundary_type_map.values())]
  sequence_sheets_list.append(points_sheet_name)

  xls = pd.ExcelFile(data_file)
  points = pd.read_excel(xls, points_sheet_name)

  points = points[['id', 'boundary_type', 'Station']]
  result = pd.DataFrame({"id":points['id']})
  
  timeseries = []
  for index, row in points.iterrows():
    boundary_map = boundary_type_map[str(row['boundary_type'])]
    station_name_row = boundary_map["station_name_row"]-2
    first_data_row_conf = boundary_map["first_data_row"]-2
    time_column = boundary_map["time_column"]-1
    # metric_sheet = pd.read_excel(xls, boundary_map["sheet_name"], parse_dates=[time_column], 
    #                              date_format=app.get_custom_setting("datetime_format"))
    metric_sheet = pd.read_excel(xls, boundary_map["sheet_name"])

    station_name = str(row["Station"]).upper()
    if True:
      times = metric_sheet.iloc[first_data_row_conf:,time_column].tolist()
      if isinstance(times[0], str):
        times = list(map(lambda x:datetime.strptime(x, app.get_custom_setting(name="datetime_format")),times))
      
      np_times = np.array(times)

    first_data_row = np.argmax(np_times >= start_datetime) + first_data_row_conf if start_datetime is not None else first_data_row_conf
    last_data_row = np.argmax(np_times > end_datetime) + first_data_row_conf if end_datetime is not None else -1

    print(first_data_row, last_data_row)

    station_array =\
    metric_sheet.iloc[[station_name_row]].values.flatten().tolist() if station_name_row >= 0 \
    else list(metric_sheet.columns)

    station_array = list(map(lambda x:str(x).upper(),station_array))
    series_col = station_array.index(station_name) if station_name in station_array else -1

    series = metric_sheet.iloc[first_data_row: last_data_row,series_col].tolist() if series_col>= 0 else []
    series = "\n".join(map(lambda x:str(x),series))
    timeseries.append(series)
  
  result["timeseries"]= timeseries
  
  result.to_csv("./timeseries.csv",index=False)

  # points.to_csv("./ids.csv",index=False)

  # res = dss1_final(saved_file,None,None, None)
  # res.to_csv('./result.csv')

  
  return True

def load_result():
  stations = []
  # result_file = './result.csv'
  # if os.path.isfile(result_file):
  #   dss1_df = pd.read_csv('./result.csv',skiprows=[1])
  #   for index, row in dss1_df.iterrows():
  #     station = lambda: None
  #     station.id = row['Matram']
  #     station.latitude = row['latitude']
  #     station.longitude = row['longitude']
  #     station.WQI_I = row['WQI_I']
  #     station.WQI_II = row['WQI_II']
  #     station.WQI_III = row['WQI_III']
  #     station.WQI_IV = row['WQI_IV']
  #     station.WQI_V = row['WQI_V']
  #     station.WQI = row['WQI']
  #     station.WQI_Level = row['WQI_Level']
  #     station.WQI_Color = row['WQI_Color']
  #     stations.append(station)
  return stations