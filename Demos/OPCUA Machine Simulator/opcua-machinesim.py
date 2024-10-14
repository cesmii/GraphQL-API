#! /usr/bin/env python3

''' Dependenices to install:
      pip install opcua 
'''
# TODO: Migrate to new library: https://github.com/FreeOpcUa/opcua-asyncio

from opcua import Server
import datetime
#import time
import csv

# TODO: These could be command line arguments
data_file = "FestoData.csv"
server_url = "opc.tcp://localhost:62544"
server_name = "CESMII_UA_Machine_SIM"
sample_rate = 2
simulation_data = []

print("Configuring CESMII Machine Simulator OPC UA Server...")
my_ua_server = Server()
my_ua_server.set_endpoint(server_url)
my_ua_server.set_server_name("CESMII Machine Simulator")
# TODO: Add SSL certs for secure auth

# Register a new namespace to work in
my_ua_namespace = my_ua_server.register_namespace(server_name)
print("Namespace ID: {}".format(my_ua_namespace))

# Find the "Objects" folder to attach a new object to
my_ua_node = my_ua_server.get_objects_node()
print("Objects Node ID: ", my_ua_node)

# Create a new object
my_ua_nsname = data_file.replace(".csv", "")
my_ua_object = my_ua_node.add_object(my_ua_namespace, my_ua_nsname)
print(my_ua_nsname + " Object ID:", my_ua_object)
print()

# Read in simulation data
with open(data_file, newline='') as f:
      # Read the first line of the CSV file to create attributes
      print("Adding attributes...")
      csv_reader = csv.reader(f)
      csv_headings = next(csv_reader)
      column_names = list(csv_headings)
      opc_attribs = []
      for i in column_names:
            print("- " + i.strip())
            if i.strip() == "Timestamp":
                  new_attrib = my_ua_object.add_variable(my_ua_namespace, i.strip(), datetime.datetime.now())
            else:
                  new_attrib = my_ua_object.add_variable(my_ua_namespace, i.strip(), 0.0)
            opc_attribs.append(new_attrib)

      # Read the rest of the rows into memory
      for row in csv_reader:
            simulation_data.append(row)

try:
      print()
      print("Starting CESMII Simulation Server...")
      my_ua_server.start()
      print()
      print("Generating Data...")
      j = 0

      while True:
            # TODO: Loop through the lines of the CSV file, restarting at end, and send values for each column
            if j >= len(simulation_data) - 1:
                  j = 0
            else:
                  j += 1
            
            print()
            print("Simulated values row " + str(j) + "...")
            curr_vals = list(simulation_data[j])
            curr_col = 0
            for val in curr_vals:
                  curr_name = column_names[curr_col].strip()
                  if curr_name.strip() == "Timestamp":
                        use_val = datetime.datetime.now()
                  else:
                        use_val = val
                        
                  print (column_names[curr_col].strip() + ": " + str(use_val))
                  #Update the attribute values for my object
                  opc_attribs[curr_col].set_value(use_val)
                  curr_col += 1

            #attrib_load.set_value(cpu.load)
            #attrib_press.set_value(computer.virtual_memory.used_percent)
            #attrib_time.set_value(datetime.datetime.now())

            #print ("Current values: ", attrib_load.get_value(), attrib_press.get_value(), attrib_time.get_value(), attrib_toggler.get_value())
            time.sleep(sample_rate)

finally:
      my_ua_server.stop()
      print("CESMII Simulation Server Offline")





