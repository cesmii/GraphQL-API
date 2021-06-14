from utils import *

import time

def simulate_stepwise(lines, topic, mqtt_client):
    """Simulate fill level changes in the input file

    [description]
    
    Arguments:
        topic {str} -- mqtt topic name
        mqtt_client {class} -- mqtt class
    """
    try:
        while True:
            count = 0
            for line in lines:
                count += 1
                volume = round(float(line.strip()), 1)
                jsonobj = {}
                jsonobj["stepwise"] = 1
                jsonobj["volume"] = volume
                jsonobj["temperature"] = volume * 2 + 3
                mqtt_publish(str(jsonobj), topic, mqtt_client)
                time.sleep(1)
    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()
