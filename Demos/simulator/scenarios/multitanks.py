from itertools import count
import json
from utils import *

import paho.mqtt.client as mqtt
import random
import time
import config
import threading

tube_flowrate = 5.0
MAX_VOLUME = config.one_tank_size
tank_amount = config.tank_amount
tanks_relations = config.tanks_relations
tanks_sizes = config.tanks_sizes
tanks_fill_level = config.tanks_fill_level
cavitations = config.cavitations
leaks = config.leaks
tank_name_prefix = config.tank_name_prefix
tanks_serialNumber = random.sample(range(1,100), tank_amount)
cavitation_movement = [4, 0.5, 1.5, 5, 1, 4.6, 0.8, 6]

"""from pynput import keyboard
def on_press(key):
    try:
        if key.char == '0':
            config.leaks[1] = True
            print(config.leaks)
        if key.char == '1':
            config.cavitations[1] = True
            print(config.cavitations)
    except AttributeError:
        print('special key {0} pressed'.format(
            key))

def on_release(key):
    print('{0} released'.format(
        key))
    if key == keyboard.Key.esc:
        # Stop listener
        return False"""

# Collect events until released


def checkChangeValue():
    global value
    while True:
        newValue = input()
        print(config.leaks)
        if newValue == "leak":
            
            config.leaks[1] = True
            print(config.leaks)

def updateTank(tank_num, volume, mqtt_client):
    topic = tank_name_prefix+str(tank_num+1)
    jsonobj = make_json_multitanks(topic, tank_num)
    jsonobj["volume"] = volume
    jsonobj["temperature"] = volume * 2 + 32
    mqtt_publish(json.dumps(jsonobj), topic, mqtt_client)

def doTank(tank_volume, flow_rate, limit, tank, mqtt_client):
    while tank_volume!=limit:
        if cavitations[tank]:
            flow_rate = round(random.uniform(1.2, flow_rate//2), 1) * 2
        tank_volume += flow_rate
        tank_volume = round(tank_volume, 1)
        tank_volume = min(tank_volume, tanks_sizes[tank])
        tank_volume = max(tank_volume, 0.0)
        updateTank(tank, tank_volume, mqtt_client)        
        time.sleep(1.5)
    tanks_fill_level[tank] = tank_volume



def drainandfill(drainTank, fillTank, mqtt_client):
    time.sleep(1.5)
    tankD_volume = tanks_fill_level[drainTank]
    flowrate = 5.0
    cavitation_counter = 0
    len_cavitation = len(cavitation_movement)
    while tankD_volume != 0.0:
        if cavitations[drainTank]:
            flowrate = cavitation_movement[cavitation_counter]
            cavitation_counter = (cavitation_counter+1) % len_cavitation
        flowrate = min(flowrate, tankD_volume)
        tankD_volume -= flowrate
        tankD_volume = round(tankD_volume, 1)
        tanks_fill_level[drainTank] = tankD_volume
        updateTank(drainTank, tankD_volume, mqtt_client)
        
        if fillTank: flowrate2 = round(flowrate/len(fillTank), 1)
        for tank in fillTank:
            if leaks[tank]: 
                flowrate2 = round(random.uniform(0, flowrate), 1)
            tanks_fill_level[tank] += flowrate2
            tanks_fill_level[tank] = round(tanks_fill_level[tank], 1)
            updateTank(tank, tanks_fill_level[tank], mqtt_client)
            time.sleep(1.5)
        time.sleep(1.5)
    
    


def flow_with_leak(topic, mqtt_client):
    try:
        for tank in range(tank_amount):
            topic = tank_name_prefix+str(tank)
            jsonobj={"tank_name": topic, "volume":0, "temperature":0, "size": tanks_sizes[tank], "one_tank_model": 0}
            mqtt_publish(str(jsonobj), topic, mqtt_client)
        time.sleep(tank_amount*1.5)
        start_abnormal = random.randint(3, 10)
        counter = 0
        while True:
            leak_count = random.randint(1, tank_amount-1)
            leak_tanks = random.sample(range(1,tank_amount), leak_count)
            for tank in leak_tanks:
                leaks[tank] = True
            print(leaks)
            doTank(0.0, 5.0, tanks_sizes[0], 0, mqtt_client)
            for i in range(tank_amount-1):
                drainandfill(i, tanks_relations[i], mqtt_client)
            doTank(tanks_fill_level[tank_amount-1], -5.0, 0.0, tank_amount-1, mqtt_client)
    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()

def flow_with_cavitation(topic, mqtt_client):
    try:
        while True:
            doTank(0.0, 5.0, 20.0, "Mytank0", mqtt_client)
            for i in range(6):
                if i==1:
                    drainandfill(i, i+1, True, False, mqtt_client)
                else:
                    drainandfill(i, i+1, False, False, mqtt_client)
            doTank(20.0, -5.0, 0.0, "Mytank6", mqtt_client)
    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()

def normalflow(topic, mqtt_client):
    def get_input():
        while True:
            problem = input()
            if problem == "cavitation":
                config.cavitations[1] = True
                print(config.cavitations)
            if problem == "leak":
                config.leaks[4] = True
                print(config.leaks)
    def tank_op():
        for tank in range(tank_amount):
            topic = tank_name_prefix+str(tank+1)
            jsonobj = make_json_multitanks(topic, tank)
            jsonobj["serialNumber"] = str(tanks_serialNumber[tank])
            mqtt_publish(json.dumps(jsonobj), topic, mqtt_client)
        time.sleep(tank_amount*3)
        while True:
            doTank(0.0, 5.0, tanks_sizes[0], 0, mqtt_client)
            for i in range(tank_amount-1):
                drainandfill(i, tanks_relations[i], mqtt_client)
            doTank(tanks_fill_level[tank_amount-1], -5.0, 0.0, tank_amount-1, mqtt_client)
    try:
        t1 = threading.Thread(target=get_input)
        t2 = threading.Thread(target=tank_op)
    
        # starting thread 2
        t2.start()
        # starting thread 1
        t1.start()
        
        
        
    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()
