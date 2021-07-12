from utils import *

import paho.mqtt.client as mqtt
import random
import time

tank_volume = 20.0

def fillandleak_tank(topic, mqtt_client, flow_rate_fill, flow_rate_leak):

    global tank_volume
    tank_volume = tank_volume + flow_rate_fill - flow_rate_leak
    tank_volume = round(max(tank_volume, 0.0), 1)

    jsonobj={'flowrate':0, 'volume':0, 'temperature':0}
    jsonobj["volume"] = tank_volume
    jsonobj["temperature"] = tank_volume * 2 + 3
    jsonobj["flowrate"] = flow_rate_fill - flow_rate_leak
    mqtt_publish(str(jsonobj), topic, mqtt_client)

    print("flow_rate_fill: " + str(flow_rate_fill), "flow_rate_leak: " + str(flow_rate_leak))
    time.sleep(1)

def simulate_fillandleak(flow_rate_fill, flow_rate_leak, topic, mqtt_client):
    """Simulate fill while leaking with constant flow rate

    [description]
    
    Arguments:
        flow_rate_fill {float} -- the flow rate at which the tank is filled
        flow_rate_leak {float} -- the flow rate at which the tank is leaking
        topic {str} -- mqtt topic name
        mqtt_client {class} -- mqtt class
    """

    try:
        while True:
            fillandleak_tank(topic, mqtt_client, flow_rate_fill, flow_rate_leak);

    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()
