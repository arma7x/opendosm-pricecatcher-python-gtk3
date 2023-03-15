import os
import requests
from pathlib import Path
from urllib.parse import urlparse
from datetime import date

base_url = "https://storage.googleapis.com/dosm-public-pricecatcher"

def get_parquet_content_length(url):
  response = requests.head(url)
  if ('Content-Length' in response.headers):
    return int(response.headers.get('Content-Length'))
  else:
    return 0

def download_parquet(url):
  print(f'Downloading: {url}')
  filename = urlparse(url).path.split('/')[-1]
  response = requests.get(url)
  Path(os.path.join(os.getcwd(), "parquets")).mkdir(parents=True, exist_ok=True)
  with open(os.path.join(os.getcwd(), "parquets", filename), "wb") as f:
    f.write(response.content)

def get_cached_parquet_file_size(path):
  if (os.path.isfile(path) == False):
    return 0
  return os.path.getsize(path)

def get_local_parquet(name):
  return os.path.join(os.getcwd(), "parquets", name)

def get_item_parquet():
  path = get_local_parquet("lookup_item.parquet")
  itemCachedFileSize = get_cached_parquet_file_size(path)
  itemContentLength = get_parquet_content_length(base_url + "/lookup_item.parquet")
  if ((itemCachedFileSize != itemContentLength) or itemCachedFileSize == 0 or itemContentLength == 0):
    download_parquet(base_url + "/lookup_item.parquet")
  return path

def get_premise_parquet():
  path = get_local_parquet("lookup_premise.parquet")
  premiseCachedFileSize = get_cached_parquet_file_size(path)
  premiseContentLength = get_parquet_content_length(base_url + "/lookup_premise.parquet")
  if ((premiseCachedFileSize != premiseContentLength) or premiseCachedFileSize == 0 or premiseContentLength == 0):
    download_parquet(base_url + "/lookup_premise.parquet")
  return path


def get_pricecatcher_parquet(ym = None):
  if (ym == None):
    today = date.today()
    ym = f'{today.year}-{today.month:02d}'
  path = get_local_parquet(f'pricecatcher_{ym}.parquet')
  priceCatcherCachedFileSize = get_cached_parquet_file_size(path)
  priceCatcherContentLength = get_parquet_content_length(f'{base_url}/pricecatcher_{ym}.parquet')
  if ((priceCatcherCachedFileSize != priceCatcherContentLength) or priceCatcherCachedFileSize == 0 or priceCatcherContentLength == 0):
    download_parquet(f'{base_url}/pricecatcher_{ym}.parquet')
  return path

if (__name__ == '__main__'):
  try:
    get_item_parquet()
    get_premise_parquet()
    get_pricecatcher_parquet(None)
  except Exception as e:
    print(e)
