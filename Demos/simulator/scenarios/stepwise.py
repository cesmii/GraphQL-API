from utils import *

import time

def simulate_stepwise(lines, topic, mqtt_client):
    try:
        while True:
            count = 0
            for line in lines:
                count += 1
                mqtt_publish(line.strip(), topic, mqtt_client)
                time.sleep(1)
    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()
