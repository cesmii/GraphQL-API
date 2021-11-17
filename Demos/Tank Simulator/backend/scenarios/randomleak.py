from utils import *
import paho.mqtt.client as mqtt
import random, config
import time, json

# max_tank_volume = 100
change_interval = 5
interval_count = 0
current_flow_rate = 1.0
tank_volume = 20.0
pre_volume = 20.0
MAX_VOLUME = config.one_tank_size
tank_name = config.tank_name_prefix+"1"

def change_flow_rate():
    global current_flow_rate
    current_flow_rate = random.randint(1, 10)

def leak_tank(topic, mqtt_client):
    time.sleep(2)
    global interval_count
    global tank_volume
    global pre_volume

    topic = tank_name
    tank_volume -= float(current_flow_rate)
    set_interval_count()
    tank_volume = max(tank_volume, 0)

    flowrate = tank_volume - pre_volume
    pre_volume = tank_volume

    jsonobj=make_default_json(tank_name, 0)
    jsonobj["volume"] = tank_volume
    jsonobj["temperature"] = tank_volume * 2 + 3
    jsonobj["flowrate"] = flowrate
    mqtt_publish(json.dumps(jsonobj), topic, mqtt_client)

    print("flow_rate: " + str(float(current_flow_rate)))
    time.sleep(1)

def set_interval_count(): 
    global change_interval
    global interval_count

    if interval_count == change_interval:
        change_flow_rate()
        interval_count = 0

    interval_count += 1

def simulate_randomleak(topic, mqtt_client):
    """Simulate random leak speeds that change every 5 seconds

    [description]

    Arguments:
        topic {str} -- mqtt topic name
        mqtt_client {class} -- mqtt class
    """

    try:
        topic = tank_name
        jsonobj=make_default_json(tank_name, 0)
        mqtt_publish(json.dumps(jsonobj), topic, mqtt_client)
        while True:
            leak_tank(topic, mqtt_client)

    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()