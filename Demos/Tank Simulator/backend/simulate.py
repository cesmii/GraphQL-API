#!/usr/bin/python3
from hashlib import new
from scenarios import *
from utils import *

import config   #copy config-example.py to config.py and set values
import sys
import time
import random, config
import uuid
import paho.mqtt.client as mqtt

mqtt_broker = config.mqtt["broker"]
uuid = str(uuid.uuid4())[:8]
mqtt_clientid = config.mqtt["clientprefix"] + uuid
tube_flowrate = 1.0


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
    function_rate = "0"
    #Figure out what arguments were specified
    print(args)
    for arg in args:
        if count == 1:
            config = arg
            topic = arg
        elif count == 2:
            simulation = arg
        elif count == 3:
            if simulation == "functionchange":
                function_rate = arg
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
    elif simulation == "randomfill":
        simulate_randomfill(topic, mqtt_client)
    elif simulation == "fillthendrain":
        simulate_fillthendrain(topic, mqtt_client)
    elif simulation == "normalflow":
        normalflow(topic, mqtt_client)
    elif simulation == "flow_with_leak":
        flow_with_leak(topic, mqtt_client)
    elif simulation == "flow_with_cavitation":
        flow_with_cavitation(topic, mqtt_client)
    elif simulation == "randomleak":
        simulate_randomleak(topic, mqtt_client)
    elif simulation == "functionchange":
        simulate_functionchange(function_rate, set_fill, topic, mqtt_client)
    elif simulation == "cavitation":
        cause_cavitation(topic, mqtt_client)
    elif simulation == "leakage":
        cause_leakage(topic, mqtt_client)

    randnum = random.randint(1, len(Lines))  
    randomtanks = sorted(random.sample(range(0,len(Lines)), randnum))
    Lines = [float(n) for n in Lines]
    if simulation == "oneleak":
        simulate_oneleak(Lines, mqtt_client)
    elif simulation == "onestuck":
        simulate_onestuck(Lines, mqtt_client)
    elif simulation == "oneflood":
        simulate_oneflood(Lines, mqtt_client)
    elif simulation == "leakandstuck":
        simulate_leakandstuck(Lines, mqtt_client)
    elif simulation == "floodandleak":
        simulate_floodandleak(Lines, mqtt_client)
    elif simulation == "floodandstuck":
        simulate_floodandstuck(Lines, mqtt_client)
    elif simulation == "randnumleak":
        simulate_randnumleak(randomtanks, randnum, Lines, mqtt_client)
    elif simulation == "randnumflood":        
        simulate_randnumflood(randomtanks, randnum, Lines, mqtt_client)
    elif simulation == "randnumstuck":
        simulate_randnumstuck(randomtanks, randnum, Lines, mqtt_client)



if __name__ == "__main__":
    print()
    print ("CESMI IIOT Simulator")
    print ("=============================")
    print ("")
    main(sys.argv)