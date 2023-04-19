import configparser
import requests
from requests.auth import HTTPBasicAuth

config = configparser.RawConfigParser()   
config.read_file(open(r'config.ini'))

login_url = 'https://api2.watttime.org/v2/login'
token = requests.get(login_url, auth=HTTPBasicAuth(config.get('WattTime', 'username'), config.get('WattTime', 'password'))).json()['token']

index_url = 'https://api2.watttime.org/index'
headers = {'Authorization': 'Bearer {}'.format(token)}
params = {'ba': 'CAISO_NORTH'}
rsp=requests.get(index_url, headers=headers, params=params)
print(rsp.text)
