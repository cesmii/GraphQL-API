from itertools import count
from utils import *

import paho.mqtt.client as mqtt
import random
import time
import config

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


from pynput import keyboard
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
        return False

# Collect events until released


def checkChangeValue():
    global value
    while True:
        newValue = input()
        print(config.leaks)
        if newValue == "leak":
            
            config.leaks[1] = True
            print(config.leaks)


def doTank(tank_volume, flow_rate, limit, tank, mqtt_client):
    while tank_volume!=limit:
        if cavitations[tank]:
            flow_rate = round(random.uniform(1.2, flow_rate//2), 1) * 2
        tank_volume += flow_rate
        tank_volume = round(tank_volume, 1)
        tank_volume = min(tank_volume, tanks_sizes[tank])
        tank_volume = max(tank_volume, 0.0)
        jsonobj={'tank_name': tank_name_prefix+str(tank), 'volume':0, 'temperature':0, 'size': tanks_sizes[tank],  'one_tank_model': 0}
        jsonobj["volume"] = tank_volume
        jsonobj["temperature"] = tank_volume * 2 + 32
        #jsonobj["flowrate"] = tube_flowrate
        mqtt_publish(str(jsonobj), tank_name_prefix+str(tank), mqtt_client)
        time.sleep(2)
    tanks_fill_level[tank] = tank_volume
def drainandfill(drainTank, fillTank, mqtt_client):
    time.sleep(2)
    tankD_volume = tanks_fill_level[drainTank]
    flowrate = 5.0
    while tankD_volume != 0.0:
        if cavitations[drainTank]:
            flowrate = round(random.uniform(1.4, flowrate//2), 1) * 2
        flowrate = min(flowrate, tankD_volume)
        tankD_volume -= flowrate
        tankD_volume = round(tankD_volume, 1)
        tanks_fill_level[drainTank] = tankD_volume
        jsonobj={'tank_name': '', 'volume':0, 'temperature':0, 'size': tanks_sizes[drainTank],  'one_tank_model': 0}
        jsonobj['tank_name'] = tank_name_prefix+str(drainTank)
        jsonobj["volume"] = tankD_volume
        jsonobj["temperature"] = tankD_volume * 2 + 32
        mqtt_publish(str(jsonobj), tank_name_prefix+str(drainTank), mqtt_client)
        
        if fillTank: flowrate2 = round(flowrate/len(fillTank), 1)
        for tank in fillTank:
            if leaks[tank]: 
                flowrate2 = round(random.uniform(0, flowrate), 1)
            tanks_fill_level[tank] += flowrate2
            tanks_fill_level[tank] = round(tanks_fill_level[tank], 1)
            jsonobj['tank_name'] = tank_name_prefix+str(tank)
            jsonobj["volume"] = tanks_fill_level[tank]
            jsonobj["temperature"] = tanks_fill_level[tank] * 2 + 32
            jsonobj['size'] = tanks_sizes[tank]
            mqtt_publish(str(jsonobj), tank_name_prefix+str(tank), mqtt_client)
            time.sleep(2)
        time.sleep(2)
    
    
    

def flow_with_leak(topic, mqtt_client):
    try:
        for tank in range(tank_amount):
            topic = tank_name_prefix+str(tank)
            jsonobj={'tank_name': topic, 'volume':0, 'temperature':0, 'size': tanks_sizes[tank], 'one_tank_model': 0}
            mqtt_publish(str(jsonobj), topic, mqtt_client)
        time.sleep(tank_amount*3)
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

    try:
        listener = keyboard.Listener(
            on_press=on_press,
            on_release=on_release)
        listener.start()
        for tank in range(tank_amount):
            topic = tank_name_prefix+str(tank)
            jsonobj={'tank_name': topic, 'volume':0, 'temperature':0, 'size': tanks_sizes[tank], 'one_tank_model': 0, 'serialNumber': str(tanks_serialNumber[tank])}
            mqtt_publish(str(jsonobj), topic, mqtt_client)
        time.sleep(tank_amount*3)
        print(config.leaks)
        while True:
            doTank(0.0, 5.0, tanks_sizes[0], 0, mqtt_client)
            for i in range(tank_amount-1):
                drainandfill(i, tanks_relations[i], mqtt_client)
            doTank(tanks_fill_level[tank_amount-1], -5.0, 0.0, tank_amount-1, mqtt_client)
    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()



def simulate_oneflood(lines, mqtt_client):
    """Simulate having one of the tanks flooding that randomly increases fill level

    [description]
    
    Arguments:
        lines {[float]} -- the original fill levels of each tank 
        mqtt_client {class} -- mqtt class
    """
    try:
        while True:
            count = 0
            flood_tube = 2
            flow_in = 1
            flow_out = 1
            topic = "Mytank"
            while count < len(lines):
                lines[count] = lines[count] + flow_in - flow_out
                jsonobj={'volume':0, 'temperature':0, 'leak':0, 'stuck':0, 'flood':0}
                jsonobj["flood"] = 0
                if count == flood_tube:
                    lines[count] += random.uniform(0.0, 1.0)
                    jsonobj["flood"] = 1
                lines[count] = round(lines[count], 1)
                lines[count] = min(lines[count],MAX_VOLUME)
                jsonobj["volume"] = lines[count]
                jsonobj["temperature"] = lines[count] * 2 + 3
                mqtt_publish(str(jsonobj), topic + str(count), mqtt_client)
                count += 1
            time.sleep(1)
                    
    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()

def simulate_oneleak(lines, mqtt_client):
    """Simulate having one of the tanks leaking that randomly decreases the fill level

    [description]
    
    Arguments:
        lines {[float]} -- the original fill levels of each tank 
        mqtt_client {class} -- mqtt class
    """
    try:
        while True:
            count = 0
            leak_tube = 2
            flow_in = 1
            flow_out = 1
            topic = "Mytank"
            while count < len(lines):
                jsonobj={'volume':0, 'temperature':0, 'leak':0, 'stuck':0, 'flood':0}
                jsonobj["leak"] = 0
                if count == leak_tube:
                    lines[count] -= round(random.uniform(0.0, tube_flowrate), 1)
                    jsonobj["leak"] = 1
                lines[count] = max((lines[count] + flow_in - flow_out), 0.0)
                lines[count] = round(lines[count], 1)
                lines[count] = min(lines[count],MAX_VOLUME)
                jsonobj["volume"] = lines[count]
                jsonobj["temperature"] = lines[count] * 2 + 3.0
                mqtt_publish(str(jsonobj), topic + str(count), mqtt_client)
                count += 1
            time.sleep(1)
                    
    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()

def simulate_onestuck(lines, mqtt_client):
    """Simulate having one of the tanks stuck that doesn't flow out to the next tank

    [description]
    
    Arguments:
        lines {[float]} -- the original fill levels of each tank 
        mqtt_client {class} -- mqtt class
    """
    try:
        while True:
            count = 0
            stuck_tube = 2
            flow_in = 1
            flow_out = 1
            topic = "Mytank"
            while count < len(lines):
                #time.sleep(1)
                jsonobj={'volume':0, 'temperature':0, 'leak':0, 'stuck':0, 'flood':0}
                if count == stuck_tube:
                    lines[count] += flow_in
                    lines[count] = min(lines[count],MAX_VOLUME)
                    jsonobj["stuck"] = 1
                    jsonobj["volume"] = lines[count]
                    jsonobj["temperature"] = lines[count] * 2 + 3.0

                    mqtt_publish(str(jsonobj), topic + str(count), mqtt_client)
                    count += 1
                    while count < len(lines):
                        lines[count] -= flow_out
                        lines[count] = max(lines[count], 0.0)
                        lines[count] = min(lines[count],MAX_VOLUME)
                        jsonobj["stuck"] = 0
                        jsonobj["volume"] = lines[count]
                        jsonobj["temperature"] = lines[count] * 2 + 3.0
                        mqtt_publish(str(jsonobj), topic + str(count), mqtt_client)
                        count += 1
                else:
                    lines[count] = lines[count] + flow_in - flow_out
                    lines[count] = min(lines[count],MAX_VOLUME)
                    jsonobj["stuck"] = 0
                    jsonobj["volume"] = lines[count]
                    jsonobj["temperature"] = lines[count] * 2 + 3.0
                    mqtt_publish(str(jsonobj), topic + str(count), mqtt_client)
                    count += 1
            time.sleep(1)
    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()

def simulate_leakandstuck(lines, mqtt_client):
    """Simulate having one of the tanks leaking that randomly decreases the fill level,
       and one of the tanks stuck that doesn't flow out to the next tank

    [description]
    
    Arguments:
        lines {[float]} -- the original fill levels of each tank 
        mqtt_client {class} -- mqtt class
    """
    try:
        while True:
            count = 0
            leak_tube = 2
            stuck_tube = 5
            flow_in = 1
            flow_out = 1
            topic = "Mytank"
            jsonobj={'volume':0, 'temperature':0, 'leak':0, 'stuck':0, 'flood':0}
            while count < len(lines):
                if count == leak_tube:
                    lines[count] = lines[count] + flow_in - flow_out
                    lines[count] -= round(random.uniform(0.0, tube_flowrate), 1)
                    lines[count] = round(max(lines[count], 0.0), 1)
                    lines[count] = min(lines[count],MAX_VOLUME)
                    jsonobj["leak"] = 1
                    jsonobj["stuck"] = 0
                    jsonobj["volume"] = lines[count]
                    jsonobj["temperature"] = lines[count] * 2 + 3.0
                    mqtt_publish(str(jsonobj), topic + str(count), mqtt_client)
                    count += 1
                elif count == stuck_tube:
                    lines[count] += flow_in
                    lines[count] = round(lines[count], 1)
                    lines[count] = min(lines[count],MAX_VOLUME)
                    jsonobj["leak"] = 0
                    jsonobj["stuck"] = 1
                    jsonobj["volume"] = lines[count]
                    jsonobj["temperature"] = lines[count] * 2 + 3
                    mqtt_publish(str(jsonobj), topic + str(count), mqtt_client)
                    count += 1
                    while count < len(lines):
                        lines[count] -= flow_out
                        lines[count] = round(max(lines[count], 0.0), 1)
                        lines[count] = min(lines[count],MAX_VOLUME)
                        jsonobj["leak"] = 0
                        jsonobj["stuck"] = 0
                        jsonobj["volume"] = lines[count]
                        jsonobj["temperature"] = lines[count] * 2 + 3.0
                        mqtt_publish(str(jsonobj), topic + str(count), mqtt_client)
                        count += 1
                        #time.sleep(1)
                else:
                    lines[count] = lines[count] + flow_in - flow_out
                    lines[count] = min(lines[count],MAX_VOLUME)
                    jsonobj["leak"] = 0
                    jsonobj["stuck"] = 0
                    jsonobj["volume"] = lines[count]
                    jsonobj["temperature"] = lines[count] * 2 + 3.0
                    mqtt_publish(str(jsonobj), topic + str(count), mqtt_client)
                    count += 1
            time.sleep(1)
    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()

def simulate_floodandleak(lines, mqtt_client):
    """Simulate having one of the tanks flooding that randomly increases the fill level,
       and one of the tanks leaking that randomly decreases the fill level

    [description]
    
    Arguments:
        lines {[float]} -- the original fill levels of each tank 
        mqtt_client {class} -- mqtt class
    """
    try:
        while True:
            count = 0
            flood_tank = 2
            leak_tank = 5
            flow_in = 1
            flow_out = 1
            topic = "Mytank"
            jsonobj={'volume':0, 'temperature':0, 'leak':0, 'stuck':0, 'flood':0}
            while count < len(lines): 
                jsonobj["flood"] = 0
                jsonobj["leak"] = 0         
                if count == flood_tank:
                    lines[count] += round(random.uniform(0.0, 1.0), 1)
                    jsonobj["flood"] = 1 
                elif count == leak_tank:
                    jsonobj["leak"] = 1
                    lines[count] -= round(random.uniform(0.0, 1.0), 1)

                lines[count] = lines[count] + flow_in - flow_out
                lines[count] = round(max(lines[count], 0.0), 1)
                lines[count] = min(lines[count],MAX_VOLUME)
                jsonobj["volume"] = lines[count]
                jsonobj["temperature"] = lines[count] * 2 + 3.0
                mqtt_publish(str(jsonobj), topic + str(count), mqtt_client)
                count += 1
            time.sleep(2)
                    
    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()

def simulate_floodandstuck(lines, mqtt_client):
    """Simulate having one of the tanks flooding that randomly increases the fill level,
       and one of the tanks stuck that doesn't flow out to the next tank

    [description]
    
    Arguments:
        lines {[float]} -- the original fill levels of each tank 
        mqtt_client {class} -- mqtt class
    """
    try:
        while True:
            count = 0
            flood_tank = 2
            stuck_tank = 5
            flow_in = 1
            flow_out = 1
            topic = "Mytank"
            jsonobj={'volume':0, 'temperature':0, 'leak':0, 'stuck':0, 'flood':0}
            while count < len(lines):
                jsonobj["flood"] = 0
                jsonobj["stuck"] = 0         
                if count == stuck_tank: 
                    lines[count] += flow_in
                    lines[count] = min(lines[count],MAX_VOLUME)
                    jsonobj["stuck"] = 1
                    jsonobj["volume"] = lines[count]
                    jsonobj["temperature"] = lines[count] * 2 + 3.0
                    mqtt_publish(str(jsonobj), topic + str(count), mqtt_client)
                    count += 1
                    while count < len(lines):
                        lines[count] -= flow_out
                        lines[count] = round(max(lines[count], 0.0), 1)
                        lines[count] = min(lines[count],MAX_VOLUME)
                        jsonobj["stuck"] = 0
                        jsonobj["volume"] = lines[count]
                        jsonobj["temperature"] = lines[count] * 2 + 3.0
                        mqtt_publish(str(jsonobj), topic + str(count), mqtt_client)
                        count += 1
                else:
                    if count == flood_tank:
                        lines[count] += random.uniform(0.0, 1.0)
                        jsonobj["flood"] = 1
                    lines[count] = lines[count] + flow_in - flow_out
                    lines[count] = round(lines[count], 1)
                    lines[count] = min(lines[count],MAX_VOLUME)
                    jsonobj["volume"] = lines[count]
                    jsonobj["temperature"] = lines[count] * 2 + 3.0
                    mqtt_publish(str(jsonobj), topic + str(count), mqtt_client)
                count += 1
            time.sleep(2)
    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()

def simulate_randnumleak(randomleaktanks, count_leak, lines, mqtt_client):
    """Simulate having random number of tanks leaking that randomly decreases the fill level

    [description]
    
    Arguments:
        lines {[float]} -- the original fill levels of each tank 
        mqtt_client {class} -- mqtt class
    """
    try:
        while True:
            count = 0
            index_leaktank = 0
            topic = "Mytank"
            jsonobj={'volume':0, 'temperature':0, 'leak':0, 'stuck':0, 'flood':0}
            while count < len(lines):
                jsonobj["leak"] = 0  
                if index_leaktank < count_leak and count == randomleaktanks[index_leaktank]:
                    jsonobj["leak"] = 1
                    lines[count] -= round(random.uniform(0.0, 1.0), 1)
                    index_leaktank += 1
                    lines[count] = round(max(lines[count], 0.0), 1)
                lines[count] = min(lines[count],MAX_VOLUME)
                jsonobj["volume"] = lines[count]
                jsonobj["temperature"] = lines[count] * 2 + 3
                mqtt_publish(str(jsonobj), topic + str(count), mqtt_client)
                count += 1
            time.sleep(1)

    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()

def simulate_randnumflood(randomfloodtanks, count_flood, lines, mqtt_client):
    """Simulate having random number of tanks flooding that randomly increases the fill level,

    [description]
    
    Arguments:
        lines {[float]} -- the original fill levels of each tank 
        mqtt_client {class} -- mqtt class
    """
    try:
        while True:
            count = 0
            index_leaktank = 0
            topic = "Mytank"
            flow_in = 1.0
            flow_out = 1.0
            jsonobj={'volume':0, 'temperature':0, 'leak':0, 'stuck':0, 'flood':0}
            while count < len(lines):  
                jsonobj["flood"] = 0
                if index_leaktank < count_flood and count == randomfloodtanks[index_leaktank]:
                    jsonobj["flood"] = 1          
                    lines[count] += round(random.uniform(0.0, 1.0), 1)
                    index_leaktank += 1
                lines[count] = lines[count] + flow_in - flow_out
                lines[count] = round(max(lines[count], 0.0), 1)
                lines[count] = min(lines[count],MAX_VOLUME)
                
                jsonobj["volume"] = lines[count]
                jsonobj["temperature"] = lines[count] * 2 + 3.0
                mqtt_publish(str(jsonobj), topic + str(count), mqtt_client)
                count += 1
            time.sleep(1)

    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()

def simulate_randnumstuck(randomstucktanks, count_stuck, lines, mqtt_client):
    """Simulate having random number of tanks leaking that randomly decreases the fill level,

    [description]
    
    Arguments:
        lines {[float]} -- the original fill levels of each tank 
        mqtt_client {class} -- mqtt class
    """
    try:
        while True:
            count = 0
            index_stucktank = 0
            flow_in = 1
            flow_out = 1
            topic = "Mytank"
            jsonobj={'volume':0, 'temperature':0, 'leak':0, 'stuck':0, 'flood':0}
            while count < len(lines):
                if index_stucktank < count_stuck and count == randomstucktanks[index_stucktank]:
                    index_stucktank += 1
                    lines[count] += flow_in
                    lines[count] = min(lines[count],MAX_VOLUME)
                    jsonobj["stuck"] = 1
                    jsonobj["volume"] = lines[count]
                    jsonobj["temperature"] = lines[count] * 2 + 3.0
                    mqtt_publish(str(jsonobj), topic + str(count), mqtt_client)
                    count += 1
                    while count < len(lines):
                        if index_stucktank < count_stuck and count == randomstucktanks[index_stucktank]:
                            jsonobj["stuck"] = 1
                            if lines[count-1] > 0 and ((count-1) != randomstucktanks[index_stucktank - 1]):
                                lines[count] += flow_in
                            index_stucktank += 1
                        else:
                            jsonobj["stuck"] = 0
                            lines[count] -= flow_out
                        lines[count] = max(lines[count], 0.0)
                        lines[count] = min(lines[count],MAX_VOLUME)
                        jsonobj["volume"] = lines[count]
                        jsonobj["temperature"] = lines[count] * 2 + 3.0
                        mqtt_publish(str(jsonobj), topic + str(count), mqtt_client)
                        count += 1
                else:
                    lines[count] = lines[count] + flow_in - flow_out
                    lines[count] = min(lines[count],MAX_VOLUME)
                    jsonobj["stuck"] = 0
                    jsonobj["volume"] = lines[count]
                    jsonobj["temperature"] = lines[count] * 2 + 3.0
                    mqtt_publish(str(jsonobj), topic + str(count), mqtt_client)
                    count += 1
            time.sleep(1)
                    
    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()
