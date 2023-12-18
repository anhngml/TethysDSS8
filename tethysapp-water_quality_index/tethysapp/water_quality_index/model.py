import pandas as pd
from datetime import timedelta
from .dss1 import dss1_final
from django.core.files.storage import FileSystemStorage

def process_data(data_file):
  saved_file = FileSystemStorage(location="/data").save(data_file.name, data_file)
  saved_file = FileSystemStorage(location="/data").path(saved_file)
  print(saved_file)
  dss1_df = pd.read_csv(saved_file,skiprows=[1])
  dss1_df["Date"] =  pd.to_datetime(dss1_df["Date"]) # convert Date field to  
  fromdate = (pd.to_datetime('today')- timedelta(days=1000))
  todate = (pd.to_datetime('today'))
  print(dss1_df.head())
  res = dss1_final(saved_file,fromdate,todate, None)
  res.to_csv('./result.csv')
  return True

def load_result():
  stations = []
  dss1_df = pd.read_csv('./result.csv',skiprows=[1])
  for index, row in dss1_df.iterrows():
    station = lambda: None
    station.id = row['Matram']
    station.latitude = row['latitude']
    station.longitude = row['longitude']
    # WQI_I,WQI_II,WQI_III,WQI_IV,WQI_V,WQI
    station.WQI_I = row['WQI_I']
    station.WQI_II = row['WQI_II']
    station.WQI_III = row['WQI_III']
    station.WQI_IV = row['WQI_IV']
    station.WQI_V = row['WQI_V']
    station.WQI = row['WQI']
    station.WQI_Level = row['WQI_Level']
    station.WQI_Color = row['WQI_Color']
    stations.append(station)
  return stations