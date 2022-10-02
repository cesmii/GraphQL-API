import time, sys, random
import config
import argparse
from pylogix import PLC
import paho.mqtt.client as paho
from smip import graphql
import json

parser = argparse.ArgumentParser()
parser.add_argument("-smip", "--smip", type=int, default=False)
args = parser.parse_args()

sample_rate = config.cip["samplerate"]
verbose = config.smip["verbose"]
do_toggle = config.toggler["toggle"]
toggle_at = config.toggler["every"]
use_toggle_at = toggle_at
last_toggle = False

print("\nCESMII 990-SM10 Data Publisher")
print("==============================")
if verbose:
        print("Verbose mode: on")
if bool(args.smip):
        print("\033[36mCESMII SMIP publishing enabled at: " + config.smip["url"] + "\033[0m")
print("Updating MQTT Broker " + str(config.mqtt["broker"]) + " with light value every " + str(sample_rate) + " seconds")
if do_toggle:
        if toggle_at == -1:
                print ("\033[33mLight will be toggled randomly\033[37m")
        else:
                print ("\033[33mLight will be toggled every " + str(toggle_at) + " samples\033[37m")
else:
        print ("\033[33mLight must be physically toggled using switch SS1\033[37m")
time.sleep(2)

#MQTT client
broker=config.mqtt["broker"]
port=config.mqtt["port"]
yellow_light_topic=config.mqtt["yellow_light_topic"]
def on_publish(client, userdata, result):
        print("Updating MQTT topic: " + yellow_light_topic)
        pass
mqtt_client= paho.Client("cesmii_990sm10_demo")
mqtt_client.on_publish = on_publish

#SMIP client
graphql = graphql(config.smip["authenticator"], config.smip["password"], config.smip["name"], config.smip["role"], config.smip["url"], verbose)
yellow_light_id = config.smip["yellow_light_id"]
def update_smip(light_on):
        print("\033[36mUpdating SMIP attribute: " + str(yellow_light_id) + "\033[0m")
        smp_query = f"""
                mutation updateTimeSeries {{
                replaceTimeSeriesRange(
                    input: {{attributeOrTagId: "{yellow_light_id}", entries: [ {{timestamp: "{graphql.make_datetime_utc()}", value: "{light_on}", status: "0"}} ] }}
                    ) {{
                    clientMutationId,
                    json
                }}
                }}
            """
        smp_response = ""

        try:
                smp_response = graphql.post(smp_query)
        except requests.exceptions.HTTPError as e:
                print("An error occured accessing the SM Platform!")
                print(e)

        if verbose:
                print("Response from SM Platform was...")
                print(json.dumps(smp_response, indent=2))
                print()

#PLC client
with PLC() as comm:
        comm.IPAddress = config.cip["plc"]
        comm.Micro800 = True
        loop_count = 0
        last_toggle = comm.Read('_IO_EM_DO_01').Value
        while True:
                # read the value of the switch
                ret = comm.Read('_IO_EM_DO_01')
                print("\nLight on:", ret.Value)

                # send the value to MQTT as a yellow light topic
                mqtt_client.connect(broker, port)
                mqtt_client.publish(yellow_light_topic, int(ret.Value))

                # send the value to smip (if enabled)
                if bool(args.smip):
                        update_smip(int(ret.Value))

                # toggle the value if requested
                if do_toggle:
                        loop_count += 1
                        if loop_count >= use_toggle_at:
                                loop_count = 0
                                if toggle_at == -1:
                                        use_toggle_at = random.randint(2, 20)
                                last_toggle = not last_toggle
                                ret = comm.Write('Demo_Switch', last_toggle)
                                print("\033[33mToggling light value:", ret.Value, ret.Status, "\033[37m")

                # wait until next sample
                time.sleep(sample_rate)
