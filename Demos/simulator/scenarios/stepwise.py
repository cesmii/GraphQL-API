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
        pre_volume = 0
        flowrate = 0
        while True:
            count = 0
            for line in lines:
                count += 1
                volume = round(float(line.strip()), 1)
                flowrate = volume - pre_volume
                jsonobj={'flowrate':0, 'volume':0, 'temperature':0}
                jsonobj["flowrate"] = flowrate
                jsonobj["volume"] = volume
                jsonobj["temperature"] = volume * 2 + 3
                mqtt_publish(str(jsonobj), topic, mqtt_client)
                time.sleep(1)
    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()
