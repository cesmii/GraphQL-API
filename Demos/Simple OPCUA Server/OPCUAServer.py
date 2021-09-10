#! /usr/bin/env python3

''' Dependenices to install via pip
      pip install pyspectator
      pip install opcua 
    Note: This generally works on Windows (including WSL) with some warnings, however pyspectator 
    requires VisualStudio C++ Build tools, and the script may require elevated execution.
'''

from opcua import Server
from pyspectator.processor import Cpu
from pyspectator.computer import Computer
from random import randint
import datetime
import time

server_url = "opc.tcp://localhost:62548"
server_name = "SIMPLE_OPCUA_SERVER"
sample_rate = 2

print("Configuring Simple OPC UA Server...")
my_ua_server = Server()
my_ua_server.set_endpoint(server_url)

# Register a new namespace to work in
my_ua_namespace = my_ua_server.register_namespace(server_name)
print("Namespace ID: {}".format(my_ua_namespace))

# Find the "Objects" folder to attach a new object to
my_ua_node = my_ua_server.get_objects_node()
print("Objects Node ID: ", my_ua_node)

# Create a new object
my_object = my_ua_node.add_object(my_ua_namespace, "MyObject")
print("MyObject ID:", my_object)

# Add some attributes (of type variable) to MyObject
attrib_load = my_object.add_variable(my_ua_namespace, "CPU Load", 0)
attrib_press = my_object.add_variable(my_ua_namespace, "Memory Pressure", 0)
attrib_time = my_object.add_variable(my_ua_namespace, "Time", 0)
# This attribute value can be written to by a client
attrib_toggler = my_object.add_variable(my_ua_namespace, "Toggle Bit", False)
attrib_toggler.set_writable()

try:
    print()
    print("Starting Simple OPC UA Server...")
    my_ua_server.start()
    print()
    print("Generating Sample Data...")

    while True:
          #Update the attribute values for my object
          cpu = Cpu(monitoring_latency=1)
          computer = Computer()

          attrib_load.set_value(cpu.load)
          attrib_press.set_value(computer.virtual_memory.used_percent)
          attrib_time.set_value(datetime.datetime.now())

          print ("Current values: ", attrib_load.get_value(), attrib_press.get_value(), attrib_time.get_value(), attrib_toggler.get_value())

          time.sleep(sample_rate)
finally:
    my_ua_server.stop()
    print("Server Offline")





