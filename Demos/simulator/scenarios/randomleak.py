from utils import *

import paho.mqtt.client as mqtt
import random
import time

# max_tank_volume = 100
change_interval = 5
interval_count = 0
current_flow_rate = 1.0
tank_volume = 20.0

def change_flow_rate():
    global current_flow_rate
    current_flow_rate = random.randint(1, 10)

def leak_tank(topic, mqtt_client, flow_rate):
    global interval_count
    global tank_volume

    tank_volume -= flow_rate
    set_interval_count()
    tank_volume = max(tank_volume, 0)
    mqtt_publish(str(tank_volume), topic, mqtt_client)

    print("flow_rate: " + str(flow_rate))
    time.sleep(1)

def set_interval_count(): 
    global change_interval
    global interval_count

    if interval_count == change_interval:
        change_flow_rate()
        interval_count = 0

    interval_count += 1

def simulate_randomleak(randomtanks, count_fill, lines, topic, mqtt_client):
    """Simulate random fill speeds

    [description]

    TODO: 
        - set a limit on the max fill
        - use n tanks
    
    Arguments:
        randomtanks {int} -- [description]
        count_fill {int} -- number of tanks
        lines {list} -- lines in the .txt file
        topic {str} -- mqtt topic name
        mqtt_client {class} -- mqtt class
    """

    try:
        while True:
            leak_tank(topic, mqtt_client, current_flow_rate)

    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()

def simulate_randomfill_original(randomtanks, count_fill, lines, topic, mqtt_client):
    try:
        while True:
            count = 0
            index_tank = 0
            while count < len(lines):              
                if index_tank < count_fill and count == randomtanks[index_tank]:
                    lines[count] += 1
                    lines[count] = min(lines[count], 10)
                    index_tank += 1
                mqtt_publish(str(lines[count]), topic, mqtt_client)
                time.sleep(1)
                count += 1
    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()