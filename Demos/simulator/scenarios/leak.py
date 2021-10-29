from os import readlink
from types import MappingProxyType
from utils import *

import paho.mqtt.client as mqtt
import config
import time
import json


MAX_VOLUME = config.one_tank_size
tank_volume = MAX_VOLUME
pre_volume = tank_volume
tank_name = config.one_tank_name
def leak_tank(mqtt_client, flow_rate, set_leak):
    time.sleep(2)
    global tank_volume
    global pre_volume
    topic = tank_name
    tank_volume -= flow_rate
    tank_volume = max(tank_volume, 0.0, set_leak)

    tank_volume = min(tank_volume, MAX_VOLUME)
    tank_volume = round(tank_volume, 1)
    flow_rate = round(tank_volume - pre_volume, 1)
    pre_volume = tank_volume

    jsonobj=make_default_json(topic, MAX_VOLUME, True)
    jsonobj["volume"] = tank_volume
    jsonobj["temperature"] = tank_volume * 2 + 3
    jsonobj["flowrate"] = -flow_rate
    mqtt_publish(json.dumps(jsonobj), topic, mqtt_client)

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
        topic = tank_name
        jsonobj=make_default_json(topic, MAX_VOLUME, True)
        mqtt_publish(json.dumps(jsonobj), topic, mqtt_client)
        while True:
            leak_tank(topic, mqtt_client, flow_rate, set_leak)

    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()
