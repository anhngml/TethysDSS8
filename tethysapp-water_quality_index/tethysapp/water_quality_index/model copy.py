import pandas as pd
from .dss1 import dss1_final
from django.core.files.storage import FileSystemStorage
import os.path

def process_data(data_file):
  saved_file = FileSystemStorage(location="/data").save(data_file.name, data_file)
  saved_file = FileSystemStorage(location="/data").path(saved_file)
  
  res = dss1_final(saved_file,None,None, None)
  res.to_csv('./result.csv')
  return True

def load_result():
  stations = []
  result_file = './result.csv'
  if os.path.isfile(result_file):
    dss1_df = pd.read_csv('./result.csv',skiprows=[1])
    for index, row in dss1_df.iterrows():
      station = lambda: None
      station.id = row['Matram']
      station.latitude = row['latitude']
      station.longitude = row['longitude']
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