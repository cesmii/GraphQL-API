from multiprocessing.dummy import Array
import datetime, time, sys, random
import config
import argparse
import paho.mqtt.client as paho
import smiputils
import mqttutils
import json, csv
import random

parser = argparse.ArgumentParser()
parser.add_argument("-smip", "--smip", type=int, default=False)
args = parser.parse_args()

verbose = config.smip["verbose"]
data_file = config.simulator["data_file"]
simulation_keys = []
simulation_data = []
machine_column = 1
station_column = 2
use_smip = False

#Show config
print("\nCESMII FIS Data Block Simulator")
print("===============================")
if verbose:
        print("Verbose mode: on")
if bool(args.smip):
        print("\033[36mCESMII SMIP publishing enabled at: " + config.smip["url"] + "\033[0m")
        use_smip = True
print("Using MQTT Broker: " + str(config.mqtt["broker"]))
print("Using Data File: " + data_file)

# Read in simulation data
with open(data_file, newline='') as f:
        # Read the first line of the CSV file to create attributes
        csv_reader = csv.reader(f)
        csv_headings = next(csv_reader)
        column_names = list(csv_headings)
        columns = 0
        # Add a timestamp column
        simulation_keys.append("Timestamp")
        # Figure out other columns
        for i in column_names:
                simulation_keys.append(i.strip())
                # Remember important columns
                if i.strip() == "Machine_ID":
                        machine_column = columns
                if i.strip() == "Station_ID":
                        station_column = columns
                columns += 1

        # Read the rest of the rows into memory
        for row in csv_reader:
                simulation_data.append(row)

# Debugging info
if verbose:
        print("rows: " + str(len(simulation_data)))
        print("machine id column: " + str(machine_column))
        print("station id column: " + str(station_column))
        time.sleep(1)
print("===============================")

# Load SMIP Data
if use_smip:
        sm_utils = smiputils.utils(config.smip["authenticator"], config.smip["password"], config.smip["name"], config.smip["role"], config.smip["url"], verbose)
        
# MQTT Client
broker=config.mqtt["broker"]
port=config.mqtt["port"]
payload_topic=config.mqtt["payload_topic_root"]
def on_publish(client, userdata, result):
        print("Updating MQTT " + str(userdata))
        pass
mqtt_client= paho.Client("cesmii_fis_demo")
mqtt_client.on_publish = on_publish

# Main Simulation Loop
sim_count = 0
machine_pool = [10]
machine_count = 1
machine_add_count = 0
while True:
        # Send a random event to the broker
        mqtt_client.connect(broker, port)

        # Shift columns to insert a timestamp
        curr_row = simulation_data[random.randint(0, len(simulation_data)-1)]
        curr_row.insert(0, int(datetime.datetime.utcnow().timestamp()))
        use_machine_column = machine_column + 1
        use_station_column = station_column + 1
        
        # Substitute simulation values
        machine_id = curr_row[use_machine_column]
        station_id = curr_row[use_station_column]

        # Start randomizing machine number after 10 events (if configured)
        if config.simulator["max_machines"] >= len(machine_pool) and sim_count >= config.simulator["wait_between_machines"] and machine_add_count >= config.simulator["wait_between_machines"]:
                # Add a new machine
                new_machine = machine_pool[len(machine_pool)-1] + 1
                machine_count += 1
                # Artificially bias the demo toward newer machines
                for i in range(machine_count):
                        machine_pool.append(new_machine)
                machine_add_count = 0
                if verbose:
                        print("Adding new machine to pool: " + str(new_machine))
                        time.sleep(1)
        else:
                machine_add_count += 1
        
        # Pick a random machine from pool to update
        machine_id = random.choice(machine_pool)
        curr_row[use_machine_column] = machine_id

        # Start randomizing station number right away (if configured)
        if config.simulator["num_stations_per_machine"] > 1 and sim_count > 1:
                station_id = random.randint(1,  config.simulator["num_stations_per_machine"])
                curr_row[use_station_column] = station_id
       
        # Build the topic, attach the payload, send to broker
        topic = payload_topic + "machine/" + str(machine_id) + "/station/" + str(station_id)
        payload_data = mqttutils.utils.make_json_payload(curr_row, simulation_keys)
        mqtt_client.user_data_set(topic)
        mqtt_client.publish(topic, payload_data)
        if verbose:
                print(topic)
                print(payload_data)

        # Send to SMIP (if configured)
        #       TODO: To make this even more real, this would be seperate code that lives in an MQTT client
        #       It would then do the SMIP update based on the MQTT publish event. For the sake of brevity
        #       both MQTT and SMIP share the incoming message and dispatch them individually in this demo.
        if use_smip:
                # Check if this equipment already exists in smip:
                machines = sm_utils.find_smip_equipment_of_type(config.smip["machine_type"])
                if verbose:
                        print (machines)
                found_machine = False
                for machine in machines:
                        if ("Machine " + str(machine_id)) == machine["displayName"]:
                                found_machine = True
                if found_machine:
                        found_station = False
                        stations = sm_utils.find_smip_equipment_of_parent(machine["id"])
                        if verbose:
                                print (stations)
                        for station in stations:
                                if ("Station " + str(station_id)) == station["displayName"]:
                                        found_station = True
                        if found_station:
                                print ("\033[33mNot implemented: Updating SMIP " + station["displayName"] + ", with ID: " + station["id"] + " on " + machine["displayName"] + ", with ID: " + machine["id"] + "\033[0m")
                        else:
                                print ("\033[31mNot implemented: Need to create equipment for station " + str(station_id) + "!\033[0m")
                else:
                        print ("\033[31mNot implemented: Need to create equipment for machine " + str(machine_id) + "!\033[0m")
                        time.sleep(1)

        # Get ready for next loop
        next_sample_rate = random.randint(config.simulator["event_sample_min"],  config.simulator["event_sample_max"])
        sim_count += 1
        if verbose:
                print("Sim #" + str(sim_count) + ", Sleeping " + str(next_sample_rate))
        time.sleep(next_sample_rate)

