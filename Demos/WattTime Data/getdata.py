import configparser
import requests
from requests.auth import HTTPBasicAuth

config = configparser.RawConfigParser()   
config.read_file(open(r'config.ini'))

login_url = 'https://api2.watttime.org/v2/login'
token = requests.get(login_url, auth=HTTPBasicAuth(config.get('WattTime', 'username'), config.get('WattTime', 'password'))).json()['token']

data_url = 'https://api2.watttime.org/v2/data'
headers = {'Authorization': 'Bearer {}'.format(token)}
params = {'ba': 'CAISO_NORTH', 
          'starttime': '2022-05-25T00:00:00-0500', 
          'endtime': '2022-05-25T08:00:00-0500'}
rsp = requests.get(data_url, headers=headers, params=params)
print(rsp.text)
