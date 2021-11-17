#!/usr/bin/python3
from ast import parse
from types import new_class
from typing import DefaultDict
import config   #copy config-example.py to config.py and set values
from datetime import datetime
import paho.mqtt.client as mqtt
from smip import graphql
import requests
import uuid
import argparse
import json
import sys
#print(sys.argv)

mqtt_broker = config.mqtt["broker"]
uuid = str(uuid.uuid4())[:8]
mqtt_clientid = config.mqtt["clientprefix"] + "GW" + uuid
mqtt_topic = ""			#This should be enumerated, not hard coded
tanks_dic = {} # {tank_name: tank_id}
attributes_dic = {} # {tank_name: {attribute:attritube_id}}
type_id = config.type_id
parent_id = config.parent_id
# Connection information for your SMIP Instance GraphQL endpoint
graphql = graphql(config.smip["authenticator"], config.smip["password"], config.smip["name"], config.smip["role"], config.smip["url"])
mqtt_topic = graphql.args.modeltype



print (f"Listening for MQTT messages on topic: {mqtt_topic} ...")


def delete_all():
	for item in tanks_dic:
		print(item)
		delete_equipment(tanks_dic[item])

def delete_equipment(equipment_id):
	smp_mutation = f'''
				mutation MyNewEquipmentMutation {{
				deleteEquipment(
					input: {{
						id: "{equipment_id}"
					}}
					){{
						equipment {{
							id
							displayName
						}}
					}}
				}}	'''
	smp_response = ""
	try:
		print("start deletion")
		smp_response = graphql.post(smp_mutation)
		print(smp_response)
	except requests.exceptions.HTTPError as e:
		print("An error occured accessing the SM Platform!")
		print(e)


def get_tank_info(equipment_type_id):
	smp_query = f'''query get_id {{
				equipments(
					filter: {{typeId: {{equalTo: "{equipment_type_id}"}}}}
					) {{
					displayName
					id
					attributes {{
					displayName
					id
					}}
				}}
				}}'''		
	smp_response = ""
	try:
		smp_response = graphql.post(smp_query)
		equipments = smp_response['data']['equipments']
		#print(equipments)
		for ele in equipments:
			tank_id = ele['id']
			tank_name = ele['displayName']
			tanks_dic[tank_name] = tank_id
			attributes_dic[tank_name] = {'id': tank_id}
			for attribute in ele['attributes']:
				attributes_dic[tank_name][attribute['displayName']] = attribute['id']
		print(attributes_dic)
		print(tanks_dic)
	except requests.exceptions.HTTPError as e:
		print("An error occured accessing the SM Platform!")
		print(e)



def create_new_equipment(equipment_name, equipment_id, parent_id):
	print("im in")
	smp_mutation = f'''
				mutation MyNewEquipmentMutation {{
				createEquipment(
					input: {{
						equipment: {{
						displayName: "{equipment_name}"
						typeId: "{equipment_id}"
						partOfId: "{parent_id}"
						}}
					}}
					) {{
						equipment {{
							id
							displayName
							attributes {{
							displayName
							id
							}}
						}}
						}}
					}}
				'''
		
	smp_response = ""
	try:
		smp_response = graphql.post(smp_mutation)
		print(smp_response)
		equipment = smp_response['data']['createEquipment']['equipment']
		equipment_id = equipment['id']
		tanks_dic[equipment_name] = equipment_id
		attributes = equipment['attributes']
		attributes_dic[equipment_name] = {}
		for each in attributes:
			attr_name = each['displayName']
			attr_id = each['id']
			attributes_dic[equipment_name][attr_name] = attr_id
		print(tanks_dic)
		print(attributes_dic)
		return int(equipment_id)
	except requests.exceptions.HTTPError as e:
		print("An error occured accessing the SM Platform!")
		print(e)
#create_new_equipment("test2")


def make_datetime_utc():
	utc_time = str(datetime.utcnow())
	time_parts = utc_time.split(" ")
	utc_time = "T".join(time_parts)
	time_parts = utc_time.split(".")
	utc_time = time_parts[0] + "Z"
	return utc_time

def update_smip(sample_value):
	print("Posting Data to CESMII Smart Manufacturing Platform...")
	print("in update")
	sample_value = json.loads(sample_value)
	tank_id = 0
	tank_name = sample_value["tank_name"]
	if tank_name in tanks_dic:
		tank_id = tanks_dic[tank_name]
	else:
		tank_id = create_new_equipment(tank_name, type_id, parent_id)
		tanks_dic[tank_name] = tank_id
	for attribute in sample_value:
		if attribute == 'tank_name': continue
		value_send = str(sample_value[attribute]) # Value to be sent to the attribute ID
		write_attribute_id = attributes_dic[tank_name][attribute] #The Equipment Attribute ID to be updated in your SMIP model
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



# python3 ga
if mqtt_topic=="clean":
	get_tank_info(type_id)
	delete_all()
	quit()
mqtt_client = mqtt.Client(mqtt_clientid)
mqtt_client.connect(mqtt_broker)



print ("MQTT Broker:  " + mqtt_broker)
print ("MQTT Client ID:  " + mqtt_clientid)
print ("Publish Topic:   " + mqtt_topic)
get_tank_info(type_id)
mqtt_client.subscribe('#')
mqtt_client.on_message=on_message
mqtt_client.loop_forever()
