from multiprocessing.dummy import Array
import datetime, time, sys, random
import config
import argparse
import paho.mqtt.client as paho
from smip import graphql
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

def debug(verbose, message, sleep=0):
        if verbose:
                print (message)
        if sleep:
                time.sleep(sleep)

#Show config
print("\nCESMII FIS Data Block Simulator")
print("===============================")
debug(verbose, "Verbose mode: on")
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
debug(verbose, "Data Rows: " + str(len(simulation_data)))
debug(verbose, "Machine ID Column: " + str(machine_column))
debug(verbose, "Station ID Column: " + str(station_column), 1)
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

        # Remember important types once discovered
        machine_type_id = None
        station_type_id = None

        # Start randomizing machine number after 10 events (if configured)
        if len(machine_pool) <= config.simulator["max_machines"] and sim_count >= config.simulator["wait_between_machines"] and machine_add_count >= config.simulator["wait_between_machines"]:
                # Add a new machine
                new_machine = machine_pool[len(machine_pool)-1] + 1
                machine_count += 1
                # Artificially bias the demo toward newer machines
                for i in range(machine_count):
                        machine_pool.append(new_machine)
                machine_add_count = 0
                debug(verbose, "Adding new machine to pool: " + str(new_machine), 1)
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
        debug(verbose, topic)
        debug(verbose, payload_data)

        # Send to SMIP (if configured)
        #       TODO: To make this even more real, this would be seperate code that lives in an MQTT client
        #       It would then do the SMIP update based on the MQTT publish event. For the sake of brevity
        #       both MQTT and SMIP share the incoming message and dispatch them individually in this demo.
        if use_smip:
                # Check if this equipment already exists in smip:
                found_machine = None
                machines = sm_utils.find_smip_equipment_of_type(config.smip["machine_type"])
                for machine in machines:
                        if ("Machine " + str(machine_id)) == machine["displayName"]:
                                found_machine = machine["id"]
                if found_machine == None:
                        if machine_type_id == None:
                                machine_type_id = sm_utils.find_smip_type_id("fis_machine")
                        print ("\033[96mDiscovered new equipment, Machine " + str(machine_id) + " of type " + str(machine_type_id) + " in Location ID: " + config.smip["parent_equipment_id"] + ". Creating...\033[0m")
                        found_machine = sm_utils.create_smip_equipment_of_typeid(config.smip["parent_equipment_id"], machine_type_id, "Machine " + str(machine_id))

                # Check if the station already exists in smip:
                found_station = None
                if found_machine:
                        stations = sm_utils.find_smip_equipment_of_parent(found_machine)
                        for station in stations:
                                if ("Station " + str(station_id)) == station["displayName"]:
                                        found_station = station["id"]
                        if found_station == None:
                                if station_type_id == None:    # Only look this up if we haven't learned it yet
                                        station_type_id = sm_utils.find_smip_type_id("fis_station")
                                print ("\033[96mDiscovered new equipment, Station " + str(station_id) + ", of type " + station_type_id + ", as child of Machine ID:" + found_machine + ". Creating...\033[0m")
                                found_station = sm_utils.create_smip_equipment_of_typeid(found_machine, station_type_id, "Station " + str(station_id))
                
                # Update actual station data
                if found_station:
                        print ("\033[96mUpdating SMIP with new data for Station ID: " + found_station + "\033[0m")
                        # find attribute ids for given station
                        smip_attribs = sm_utils.find_attributes_of_equipment_id(found_station)
                        debug(verbose, smip_attribs)

                        # map data to smip attribs, checking for outer type (Profile) safety (smip will check for data type safety)
                        payload_attribs = json.loads(payload_data.lower())
                        type_safe = True
                        ord_pos = 0
                        alias_mutates = ""
                        for smip_attrib in smip_attribs:
                                ord_pos += 1
                                attrib_name = smip_attrib['relativeName']
                                if not attrib_name in payload_attribs.keys():
                                        print("\033[33mWarning: A Type validation error has occured. Some data will not be ingested.\033[0m")
                                        type_safe = False
                                if type_safe:
                                        # form mutation aliases
                                        alias_mutates += sm_utils.build_alias_ts_mutation(str(ord_pos), smip_attrib['id'], payload_attribs[attrib_name].upper()) + "\n"
                        # form out mutation, then fire and forget
                        sm_utils.multi_tsmutate_aliases(alias_mutates)

        # Get ready for next loop
        next_sample_rate = random.randint(config.simulator["event_sample_min"],  config.simulator["event_sample_max"])
        sim_count += 1
        debug(verbose, "")
        debug(verbose, "Sim #" + str(sim_count) + " complete, Sleeping " + str(next_sample_rate) + "...")
        debug(verbose, "")
        time.sleep(next_sample_rate)