#! /usr/bin/env python3

''' Dependenices to install via pip:
      pip install asyncua
'''

import asyncio
from asyncua import ua, Server
import random
import datetime
import time

server_url = "opc.tcp://localhost:62549/simple"
server_name = "SIMPLE_OPCUA_SERVER"
sample_rate = 2

async def main():
      print("Configuring Simple OPC UA Server...")
      my_ua_server = Server()
      await my_ua_server.init()
      my_ua_server.set_endpoint(server_url)

      # Register a new namespace to work in
      my_ua_namespace = await my_ua_server.register_namespace(server_name)   
      print("Namespace ID: {}".format(my_ua_namespace))

      # Find the "Objects" folder to attach a new object to
      my_ua_node = my_ua_server.get_objects_node()
      print("Objects Node ID: ", my_ua_node)

      # Create a new ObjectType and corresponding Object instance
      mycustomobj_type = await my_ua_server.nodes.base_object_type.add_object_type(my_ua_namespace, "MyCustomObjectType")
      check_var = await mycustomobj_type.add_variable(0, "var_should_be_there_after_instantiate", 1.0)  # demonstrates instantiate
      await check_var.set_modelling_rule(True)  # make sure the variable is instansiated
      my_object = await my_ua_server.nodes.objects.add_object(my_ua_namespace, "MyCustomObjectA", mycustomobj_type.nodeid)
      print("MyObject ID:", my_object)

      # Add some attributes (of type variable) to MyObject
      #     Make sure the variable value is of the datatype you plan to send later
      attrib_rnd = await my_object.add_variable(my_ua_namespace, "Random Number", 0)  #0 since this will be an int
      attrib_time = await my_object.add_variable(my_ua_namespace, "Time", datetime.datetime.now())
      # This attribute value can be written to by a client
      attrib_toggler = await my_object.add_variable(my_ua_namespace, "Toggle Bit", False) #false since this will be a bool
      await attrib_toggler.set_writable()
      print("Added variables!")

      try:
            print()
            print("Starting Simple OPC UA Server...")
            #await my_ua_server.start()
            print()
            print("Generating Sample Data...")

            async with my_ua_server:
                  while True:
                        #Update the attribute values for my object
                        new_rnd = random.randint(0,99)
                        new_time = datetime.datetime.now()
                        new_toggle = await attrib_toggler.get_value()
                        await attrib_rnd.set_value(new_rnd)
                        await attrib_time.set_value(new_time)

                        print ("Current values: ", new_rnd, new_time, new_toggle)

                        await asyncio.sleep(sample_rate)
      finally:
            my_ua_server.stop()
            print("Server Offline")

if __name__ == "__main__":
    asyncio.run(main())




