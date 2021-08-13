#!/usr/bin/python3
from ast import parse
from types import new_class
import config   #copy config-example.py to config.py and set values
from datetime import datetime
import paho.mqtt.client as mqtt
from smip import graphql
import requests
import uuid
import argparse
import json
import sys
from sympy.parsing.sympy_parser import parse_expr

#print(sys.argv)

mqtt_broker = config.mqtt["broker"]
uuid = str(uuid.uuid4())[:8]
mqtt_clientid = config.mqtt["clientprefix"] + "GW" + uuid
mqtt_topic = "tank"			#This should be enumerated, not hard coded
tank_counter = 0
num_tanks = 0
tanksID7 = [1318, 1324, 1282, 1289, 1295, 1301, 1307] #tanks's id for multitanks simulations
tanks_dic = {"Mytank0": 1318, "Mytank1": 1324, "Mytank2": 1282, "Mytank3": 1289, "Mytank4":1295, "Mytank5":1301, "Mytank6":1307}
tanksID1 = [2128] #tanks's id for onetank simulations
tanksID = []
attributes = [] 

# Connection information for your SMIP Instance GraphQL endpoint
graphql = graphql(config.smip["authenticator"], config.smip["password"], config.smip["name"], config.smip["role"], config.smip["url"])

print (f"Listening for MQTT messages on topic: {mqtt_topic} ...")


def create_new_equipment(equipment_name="Batch Machine 001"):
	smp_mutation = f'''
				mutation MyNewEquipmentMutation {{
				createEquipment(
					input: {{
						equipment: {{
						displayName: "{equipment_name}"
						typeId: "1042"
						}}
					}}
					) {{
						equipment {{
							id
							displayName
						}}
						}}
					}}
				'''
		
	smp_response = ""
	try:
		smp_response = graphql.post(smp_mutation)
		equipment_id = smp_response['data']['createEquipment']['equipment']['id']
		return int(equipment_id)
	except requests.exceptions.HTTPError as e:
		print("An error occured accessing the SM Platform!")
		print(e)
#create_new_equipment()




def make_datetime_utc():
	utc_time = str(datetime.utcnow())
	time_parts = utc_time.split(" ")
	utc_time = "T".join(time_parts)
	time_parts = utc_time.split(".")
	utc_time = time_parts[0] + "Z"
	return utc_time

def update_smip(sample_value):
	print("Posting Data to CESMII Smart Manufacturing Platform...")
	print()
	sample_value = parse_expr(sample_value)
	tank_id = 0
	if len(tanksID) == 1:
		tank_id = tanksID1[0]
	else:
		tank_name = sample_value["tank_name"]
		if tank_name in tanks_dic:
			tank_id = tanks_dic[tank_name]
		else:
			tank_id = create_new_equipment(tank_name)
			tanks_dic[tank_name] = tank_id
	for j in range(len(attributes)):
		attribute = attributes[j] #attribute name
		value_send = str(sample_value[attribute]) # Value to be sent to the attribute ID
		write_attribute_id = str(tank_id+j+1) #The Equipment Attribute ID to be updated in your SMIP model
		smp_query = f"""
					mutation updateTimeSeries {{
					replaceTimeSeriesRange(
						input: {{attributeOrTagId: "{write_attribute_id}", entries: [ {{timestamp: "{make_datetime_utc()}", value: "{value_send}", status: "1"}} ] }}
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
	
	print("Response from SM Platform was...")
	#print(json.dumps(smp_response, indent=2))
	print()

def on_message(client, userdata, message):
	msg = str(message.payload.decode("utf-8"))
	print("Received MQTT message: " + msg)
	update_smip(msg)


print ("MQTT Broker:  " + mqtt_broker)
print ("MQTT Client ID:  " + mqtt_clientid)
print ("Publish Topic:   " + mqtt_topic)

mqtt_client = mqtt.Client(mqtt_clientid)
mqtt_client.connect(mqtt_broker)


if graphql.args.modeltype == "onetank":
	mqtt_client.subscribe('tank')	
	num_tanks = 1
	tanksID = tanksID1
	attributes = ['flowrate', 'volume', 'temperature']
elif graphql.args.modeltype == "multitanks":
	num_tanks = 7
	tanksID = tanksID7
	attributes = ['volume', 'leak', 'stuck', 'temperature', 'flood']
	"""for i in range(7):
		mqtt_client.subscribe('Mytank'+str(i))"""
	mqtt_client.subscribe('#')
mqtt_client.on_message=on_message
mqtt_client.loop_forever()
