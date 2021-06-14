from utils import *

import paho.mqtt.client as mqtt
import random
import time

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
        while True:
            for x in range(10):
                new_num = round(random.uniform(low, high), 1)
                jsonobj = {}
                jsonobj["random"] = 1
                jsonobj["volume"] = new_num
                jsonobj["temperature"] = new_num * 2 + 3
                mqtt_publish(str(jsonobj), topic, mqtt_client)
                time.sleep(1)
    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()