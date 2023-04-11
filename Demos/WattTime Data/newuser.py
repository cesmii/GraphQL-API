import configparser
import requests

config = configparser.RawConfigParser()   
config.read_file(open(r'config.ini'))

#Must register with WattTime first
register_url = 'https://api2.watttime.org/v2/register'
params = {'username': config.get('WattTime', 'username'),
         'password': config.get('WattTime', 'password'),
         'email': 'your@email.com',
         'org': 'YOURORG'}
rsp = requests.post(register_url, json=params)
print(rsp.text)
