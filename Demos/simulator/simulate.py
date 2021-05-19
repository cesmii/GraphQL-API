#!/usr/bin/python3
from scenarios import *
from utils import *

import config   #copy config-example.py to config.py and set values
import sys
import time
import random
import uuid
import paho.mqtt.client as mqtt

mqtt_broker = config.mqtt["broker"]
uuid = str(uuid.uuid4())[:8]
mqtt_clientid = config.mqtt["clientprefix"] + uuid

def main(args):
    if len(args) <= 1:
        print ("Specify unit simulation file to use")
        exit()

    count = 0
    config = ""
    simulation = "stepwise"
    num_simutank = 1
    current_flow = 1.0
    current_flow2 = 0.2
    set_fill = float('inf')
    set_leak = 0.0
    #Figure out what arguments were specified
    for arg in args:
        if count == 1:
            config = arg
            topic = arg
        elif count == 2:
            simulation = arg
            #simulation=arg
        elif count == 3:
            if simulation == "random":
                topic = arg
            else:
                current_flow = float(arg)
        elif count == 4:
            if simulation == "fill":
                set_fill = float(arg)
            elif simulation == "leak":
                set_leak = float(arg)
            elif simulation == "fillandleak":
                current_flow2 = float(arg)
        count += 1

    #Figure out what config file to use
    file1 = open(config + '.txt', 'r')
    print ("Using Config:    " + config + '.txt')
    print ("MQTT Client ID:  " + mqtt_clientid)
    print ("Publish Topic:   " + topic)
    print ("Simulation Type: " + simulation)
    print()

    #Connect to Broker
    mqtt_client = mqtt.Client(mqtt_clientid)
    mqtt_client.connect(mqtt_broker)

    #Call selected simulation function with needed values from config
    Lines = file1.readlines()
    if simulation == "random":
        high_num = 0.0
        low_num = 10000000000.0
        count_tanks=0
        for line in Lines:
            count+=1
            currNum = float(line.strip())
            if currNum > high_num:
                high_num = currNum
            if currNum < low_num:
                low_num = currNum
        simulate_random(low_num, high_num, topic, mqtt_client)
    elif simulation == "stepwise":
        simulate_stepwise(Lines, topic, mqtt_client)
    elif simulation == "fill":
        simulate_fill(current_flow, set_fill, topic, mqtt_client)
    elif simulation == "leak":
        simulate_leak(current_flow, set_leak, topic, mqtt_client) 
    elif simulation == "fillandleak":
        simulate_fillandleak(current_flow, current_flow2, topic, mqtt_client)
    elif simulation == "randomfill":
        simulate_randomfill(topic, mqtt_client)
    elif simulation == "randomleak":
        simulate_randomleak(topic, mqtt_client)


def simulate_random(low, high, topic, mqtt_client):
    try:
        while True:
            for x in range(10):
                new_num = round(random.uniform(low, high), 1)
                mqtt_publish(new_num, topic, mqtt_client)
                time.sleep(1)
    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()

if __name__ == "__main__":
    print()
    print ("CESMI IIOT Simulator")
    print ("=============================")
    print ("")
    main(sys.argv)