import configparser
import requests
from requests.auth import HTTPBasicAuth

config = configparser.RawConfigParser()   
config.read_file(open(r'config.ini'))

login_url = 'https://api2.watttime.org/v2/login'
rsp = requests.get(login_url, auth=HTTPBasicAuth(config.get('WattTime', 'username'), config.get('WattTime', 'password')))
print(rsp.json())