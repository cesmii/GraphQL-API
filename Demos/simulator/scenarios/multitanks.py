from utils import *

import paho.mqtt.client as mqtt
import random
import time

tube_flowrate = 1.0

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
                    lines[count] += round(random.uniform(0.0, 1.0), 1)
                    jsonobj["flood"] = 1
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
                    jsonobj["stuck"] = 1
                    jsonobj["volume"] = lines[count]
                    jsonobj["temperature"] = lines[count] * 2 + 3.0
                    mqtt_publish(str(jsonobj), topic + str(count), mqtt_client)
                    count += 1
                    while count < len(lines):
                        lines[count] -= flow_out
                        lines[count] = max(lines[count], 0.0)
                        jsonobj["stuck"] = 0
                        jsonobj["volume"] = lines[count]
                        jsonobj["temperature"] = lines[count] * 2 + 3.0
                        mqtt_publish(str(jsonobj), topic + str(count), mqtt_client)
                        count += 1
                else:
                    lines[count] = lines[count] + flow_in - flow_out
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
                    jsonobj["leak"] = 1
                    jsonobj["stuck"] = 0
                    jsonobj["volume"] = lines[count]
                    jsonobj["temperature"] = lines[count] * 2 + 3.0
                    mqtt_publish(str(jsonobj), topic + str(count), mqtt_client)
                    count += 1
                elif count == stuck_tube:
                    lines[count] += flow_in
                    lines[count] = round(lines[count], 1)
                    jsonobj["leak"] = 0
                    jsonobj["stuck"] = 1
                    jsonobj["volume"] = lines[count]
                    jsonobj["temperature"] = lines[count] * 2 + 3
                    mqtt_publish(str(jsonobj), topic + str(count), mqtt_client)
                    count += 1
                    while count < len(lines):
                        lines[count] -= flow_out
                        lines[count] = round(max(lines[count], 0.0), 1)
                        jsonobj["leak"] = 0
                        jsonobj["stuck"] = 0
                        jsonobj["volume"] = lines[count]
                        jsonobj["temperature"] = lines[count] * 2 + 3.0
                        mqtt_publish(str(jsonobj), topic + str(count), mqtt_client)
                        count += 1
                        #time.sleep(1)
                else:
                    lines[count] = lines[count] + flow_in - flow_out
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
                jsonobj["volume"] = lines[count]
                jsonobj["temperature"] = lines[count] * 2 + 3.0
                mqtt_publish(str(jsonobj), topic + str(count), mqtt_client)
                count += 1
            time.sleep(1)
                    
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
                    jsonobj["stuck"] = 1
                    jsonobj["volume"] = lines[count]
                    jsonobj["temperature"] = lines[count] * 2 + 3.0
                    mqtt_publish(str(jsonobj), topic + str(count), mqtt_client)
                    count += 1
                    while count < len(lines):
                        lines[count] -= flow_out
                        lines[count] = round(max(lines[count], 0.0), 1)
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
                    jsonobj["volume"] = lines[count]
                    jsonobj["temperature"] = lines[count] * 2 + 3.0
                    mqtt_publish(str(jsonobj), topic + str(count), mqtt_client)
                count += 1
            time.sleep(1)
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
                        jsonobj["volume"] = lines[count]
                        jsonobj["temperature"] = lines[count] * 2 + 3.0
                        mqtt_publish(str(jsonobj), topic + str(count), mqtt_client)
                        count += 1
                else:
                    lines[count] = lines[count] + flow_in - flow_out
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
