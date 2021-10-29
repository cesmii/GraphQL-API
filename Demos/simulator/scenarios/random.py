from hashlib import new
from utils import *

import paho.mqtt.client as mqtt
import random, config
import time
pre_volume = 0
MAX_VOLUME = config.one_tank_size

def simulate_random(low, high, topic, mqtt_client):
    """Simulate randomly changed fill level within the range from low to high

    [description]
    
    Arguments:
        low {float} -- lowest fill level in the input file
        high {float} -- highest fill level in the input file
        topic {str} -- mqtt topic name
        mqtt_client {class} -- mqtt class
    """
    try:
        global pre_volume
        flowrate = 0
        jsonobj=make_default_json(topic, MAX_VOLUME, True)
        mqtt_publish(json.dumps(jsonobj), topic, mqtt_client)
        while True:
            time.sleep(2)
            new_num = round(random.uniform(low, high), 1)
            new_num = min(new_num, MAX_VOLUME)
            flowrate = new_num - pre_volume
            pre_volume = new_num
            flowrate = round(flowrate, 1)
            
            jsonobj=make_default_json(topic, MAX_VOLUME, True)
            jsonobj["flowrate"] = flowrate
            jsonobj["volume"] = new_num
            jsonobj["temperature"] = new_num * 2 + 3
            mqtt_publish(json.dumps(jsonobj), topic, mqtt_client)
            time.sleep(1)
    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()