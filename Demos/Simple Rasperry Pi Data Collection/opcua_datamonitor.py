from opcua import ua, Server
import time
from datamonitorplus import *

uaserver = Server()
server_name = "RaspberryPi_Data_Server"
uaserver.set_endpoint("opc.tcp://0.0.0.0:62548")
uaserver.set_server_name(server_name)

ua_ns = uaserver.register_namespace(server_name)
objects_node = uaserver.get_objects_node()
data_node = objects_node.add_object(ua_ns, "rpi_data")

ua_int_temp = data_node.add_variable(ua_ns, "Internal Temperature", 0)
ua_ext_temp = data_node.add_variable(ua_ns, "External Temperature", 0)
ua_ext_humid = data_node.add_variable(ua_ns, "External Humidity", 0)

print ("Serving data to OPC UA...")
uaserver.start()

def serve_opcua():
	i_temp = measure_int_temp()
	e_temp = measure_ext_temp()
	e_humid = measure_ext_humid()

	ua_int_temp.set_value(i_temp)
	ua_ext_temp.set_value(e_temp)
	ua_ext_humid.set_value(e_humid)

try:
	while True:
		serve_opcua()
		time.sleep(1)
except KeyboardInterrupt:
	pass

uaserver.stop()
