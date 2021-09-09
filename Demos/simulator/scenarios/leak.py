from os import readlink
from types import MappingProxyType
from utils import *

import paho.mqtt.client as mqtt
import config
import time


MAX_VOLUME = config.one_tank_size
tank_volume = MAX_VOLUME
pre_volume = tank_volume
def leak_tank(topic, mqtt_client, flow_rate, set_leak):
    time.sleep(2)
    global tank_volume
    global pre_volume
    tank_volume -= flow_rate
    tank_volume = max(tank_volume, 0.0, set_leak)

    tank_volume = min(tank_volume, MAX_VOLUME)
    tank_volume = round(tank_volume, 1)
    flow_rate = round(tank_volume - pre_volume, 1)
    pre_volume = tank_volume

    jsonobj={'tank_name': topic, 'flowrate':0, 'volume':0, 'temperature':0, 'size': MAX_VOLUME, 'one_tank_model': 1}
    jsonobj["volume"] = tank_volume
    jsonobj["temperature"] = tank_volume * 2 + 3
    jsonobj["flowrate"] = -flow_rate
    mqtt_publish(str(jsonobj), topic, mqtt_client)

    print("flow_rate: " + str(flow_rate))
    time.sleep(1)

def simulate_leak(flow_rate, set_leak, topic, mqtt_client):
    """Simulate leak with constant flow rate

    [description]
    
    Arguments: 
        set_leak {float} -- the fill level where the leaking stops
        flow_rate {float} -- the flow rate at which the tank is filled
        topic {str} -- mqtt topic name
        mqtt_client {class} -- mqtt class
    """

    try:
        jsonobj={'tank_name': topic, 'flowrate':0, 'volume':0, 'temperature':0, 'size': MAX_VOLUME, 'one_tank_model': 1}
        mqtt_publish(str(jsonobj), topic, mqtt_client)
        while True:
            leak_tank(topic, mqtt_client, flow_rate, set_leak)

    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()
