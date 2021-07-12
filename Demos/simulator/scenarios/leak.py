from os import readlink
from utils import *

import paho.mqtt.client as mqtt
import random
import time

tank_volume = 20.0

def leak_tank(topic, mqtt_client, flow_rate, set_leak):

    global tank_volume
    tank_volume -= flow_rate
    tank_volume = max(tank_volume, 0.0, set_leak)

    jsonobj={'flowrate':0, 'volume':0, 'temperature':0}
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
        while True:
            leak_tank(topic, mqtt_client, flow_rate, set_leak);

    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()
