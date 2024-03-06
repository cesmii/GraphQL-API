import datetime, time, random
import config
import paho.mqtt.client as paho
import smiputils
import mqttutils
import json

def debug(verbose, message, sleep=0):
        if verbose:
                print (message)
        if sleep:
                time.sleep(sleep)
                
print("\033[36mCESMII SMIP publishing enabled at: " + config.smip["url"] + "\033[0m")
verbose = config.smip["verbose"]

def update_smip(msg):
    topic = msg.topic.split('/') # topic is of format machine/19/station/2
    machine_id = topic[1]
    station_id = topic[3]
    payload_data = msg.payload
    config.station_type_id = config.station_type_id if 'config.station_type_id' in vars() else sm_utils.find_smip_type_id("fis_station")
    config.machine_type_id = config.machine_type_id if 'config.machine_type_id' in vars() else sm_utils.find_smip_type_id("fis_machine")

    print(f"Sending data for Machine {machine_id}'s Station {station_id}")
    # Check if this equipment already exists in smip:
    found_machine = None
    machines = sm_utils.find_smip_equipment_of_type(config.smip["machine_type"])
    for machine in machines:
            if ("Machine " + str(machine_id)) == machine["displayName"]:
                    found_machine = machine["id"]
    if found_machine is None:
            print ("\033[36mDiscovered new equipment, Machine " + str(machine_id) + ", of type " + str(config.machine_type_id) + ", in Location ID: " + config.smip["parent_equipment_id"] + ". Instantiating in SMIP...\033[0m")
            found_machine = sm_utils.create_smip_equipment_of_typeid(config.smip["parent_equipment_id"], config.machine_type_id, "Machine " + str(machine_id))

    # Check if the station already exists in smip:
    found_station = None
    if found_machine:
            stations = sm_utils.find_smip_equipment_of_parent(found_machine)
            for station in stations:
                    if ("Station " + str(station_id)) == station["displayName"]:
                            found_station = station["id"]
            if found_station == None:
                    print ("\033[36mDiscovered new equipment, Station " + str(station_id) + ", of type " + config.station_type_id + ", as child of Machine ID:" + found_machine + ". Instantiating in SMIP...\033[0m")
                    found_station = sm_utils.create_smip_equipment_of_typeid(found_machine, config.station_type_id, "Station " + str(station_id))
    
    # Update actual station data
    if found_station:
            print ("Updating SMIP with new data for Station ID: " + found_station)
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

# MQTT Client
broker=config.mqtt["broker"]
port=config.mqtt["port"]
payload_topic=config.mqtt["payload_topic_root"]

def on_publish(client, userdata, result):
        print("Updating MQTT topic: " + str(userdata))

def on_message(client, userdata, msg):
    print("Message received for topic -> " + msg.topic)
    print("Updating SMIP with data")
    update_smip(msg)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code %d\n", rc)

mqtt_client = paho.Client(paho.CallbackAPIVersion.VERSION1)
#mqtt_client= paho.Client("cesmii_smip_client")
mqtt_client.on_connect = on_connect
mqtt_client.on_publish = on_publish
mqtt_client.on_message = on_message

# Load SMIP Data
sm_utils = smiputils.utils(config.smip["authenticator"], config.smip["password"], config.smip["name"], config.smip["role"], config.smip["url"], verbose)

# Main Simulation Loop
sim_count = 0


mqtt_client.connect(broker, port)
mqtt_client.subscribe("#")
mqtt_client.loop_forever()

