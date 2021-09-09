from utils import *
import config
import time
MAX_VOLUME = config.one_tank_size
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
        jsonobj={'tank_name': topic, 'flowrate':0, 'volume':0, 'temperature':0, 'size': MAX_VOLUME, 'one_tank_model': 1}
        mqtt_publish(str(jsonobj), topic, mqtt_client)
        while True:
            time.sleep(2)
            count = 0
            for line in lines:
                time.sleep(3)
                volume = round(float(line.strip()), 1)
                volume = min(volume, MAX_VOLUME)
                flowrate = volume - pre_volume
                pre_volume = volume
                jsonobj={'tank_name': topic, 'flowrate':0, 'volume':0, 'temperature':0, 'size': MAX_VOLUME, 'one_tank_model': 1}
                jsonobj["flowrate"] = flowrate
                jsonobj["volume"] = volume
                jsonobj["temperature"] = volume * 2 + 3
                mqtt_publish(str(jsonobj), topic, mqtt_client)
                
    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()
