from utils import mqtt_publish

import paho.mqtt.client as mqtt
import time

# def mqtt_publish(value, topic, mqtt_client):
#     print (topic.capitalize() + " Value: " + str(value))
#     mqtt_client.publish(topic, value)

def simulate_randomfill(randomtanks, count_fill, lines, topic, mqtt_client):
    try:
        while True:
            count = 0
            index_tank = 0
            while count < len(lines):              
                if index_tank < count_fill and count == randomtanks[index_tank]:
                    lines[count] += 1
                    lines[count] = min(lines[count], 10)
                    index_tank += 1
                mqtt_publish(str(lines[count]), topic, mqtt_client)
                time.sleep(1)
                count += 1
    except KeyboardInterrupt:
        print()
        print("Simulation stopped")
        exit()