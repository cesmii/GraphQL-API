from utils import *

import paho.mqtt.client as mqtt
import random
import time

# max_tank_volume = 100
change_interval = 5
interval_count = 0
current_flow_rate = 1.0
tank_volume = 0.0

def change_flow_rate():
    global current_flow_rate
    current_flow_rate = random.randint(1, 10)

def fill_tank(topic, mqtt_client):
    global interval_count
    global tank_volume

    tank_volume += float(current_flow_rate)
    set_interval_count()

    jsonobj = {}
    jsonobj["randomfill"] = 1
    jsonobj["ratechange"] = 1 if (interval_count == 1) else 0
    jsonobj["volume"] = tank_volume
    jsonobj["temperature"] = tank_volume * 2 + 3
    jsonobj["flowrate"] = current_flow_rate
    mqtt_publish(str(jsonobj), topic, mqtt_client)

    print("flow_rate: " + str(float(current_flow_rate)))
    time.sleep(1)

def set_interval_count(): 
    global change_interval
    global interval_count

    if interval_count == change_interval:
        change_flow_rate()
        interval_count = 0

    interval_count += 1

def simulate_randomfill(topic, mqtt_client):
    """Simulate random fill speeds that changes every 5 seconds

    [description]

    TODO: 
        - set a limit on the max fill
        - use n tanks
    
    Arguments:
        topic {str} -- mqtt topic name
        mqtt_client {class} -- mqtt class
    """

    try:
        while True:
            fill_tank(topic, mqtt_client);

    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()

