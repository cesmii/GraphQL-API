from utils import *

import paho.mqtt.client as mqtt
import random, time, json
import config
# max_tank_volume = 100
change_interval = 5
interval_count = 0
current_flow_rate = 1.0
tank_volume = 0.0
MAX_VOLUME = config.one_tank_size
drain = 0
tank_name = config.tank_name_prefix+"1"
def change_flow_rate():
    global current_flow_rate
    current_flow_rate = random.randint(1, 10)

def fill_tank(mqtt_client):

    topic = tank_name
    global tank_volume
    global drain

    while True:
        time.sleep(3)
        tempflow = round(random.uniform(1.7, 3.0), 1)
        if drain:
            tank_volume -= tempflow
        else:
            tank_volume += tempflow
        tank_volume = round(tank_volume, 1)
        tank_volume = min(tank_volume, MAX_VOLUME)
        tank_volume = max(tank_volume, 0.0)
        if tank_volume==MAX_VOLUME: drain = 1
        if tank_volume==0: drain = 0

        if drain: tempflow = -tempflow
        jsonobj=make_default_json(tank_name, 0)
        jsonobj["volume"] = tank_volume
        jsonobj["temperature"] = tank_volume * 2 + 32
        jsonobj["flowrate"] = abs(tempflow)
        mqtt_publish(json.dumps(jsonobj), topic, mqtt_client)

def simulate_fillthendrain(topic, mqtt_client):
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
        jsonobj=make_default_json(tank_name, 0)
        mqtt_publish(json.dumps(jsonobj), topic, mqtt_client)
        fill_tank(mqtt_client)

    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()

