import paho.mqtt.client as mqtt
import time
from datamonitorplus import *

client = mqtt.Client()
client.connect("localhost",1883,60)
print ("Publishing Data to broker...")

def pub_data():
	i_temp = measure_int_temp()
	e_temp = measure_ext_temp()
	e_humid = measure_ext_humid()
	client.publish("rpi/sensors", f'''{{
		"int-temperature": {i_temp},
		"ext-temperature": {e_temp},
		"ext-humidity": {e_humid}
	}}''')

try:
	while True:
		pub_data()
		time.sleep(1)
except KeyboardInterrupt:
	pass

client.disconnect()
