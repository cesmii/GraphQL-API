#! /usr/bin/env python3

''' Dependenices to install via pip:
      pip install asyncua
'''

import asyncio
from asyncua import ua, Server
from asyncua.common.structures104 import new_struct, new_enum, new_struct_field
import random
import datetime
import time

server_url = "opc.tcp://localhost:51210/example"
server_name = "SIMPLE_OPCUA_SERVER"
sample_rate = 2

async def main():
      print("Configuring Simple OPC UA Server...")
      print(server_url)
      my_ua_server = Server()
      await my_ua_server.init()
      my_ua_server.set_endpoint(server_url)

      # Register a new namespace to work in
      my_ua_namespace = await my_ua_server.register_namespace(server_name)   
      print("Namespace ID: {}".format(my_ua_namespace))

      # Find the "Objects" folder to attach a new object to
      my_ua_node = my_ua_server.get_objects_node()
      print("Objects Node ID: ", my_ua_node)

      # Create a piece of equipment
      equipment_type = await my_ua_server.nodes.base_object_type.add_object_type(my_ua_namespace, "EquipmentType")
      machineid_type = await my_ua_server.nodes.base_object_type.add_object_type(my_ua_namespace, "MachineIdentificationType")
      my_machine = await my_ua_server.nodes.objects.add_object(my_ua_namespace, "Buffer", equipment_type.nodeid)
      my_machine_id = await my_machine.add_object(my_ua_namespace, "Machine Identification", machineid_type.nodeid)
      print("New Machine:", my_machine)

      # Add some attributes (of type variable) to my_machine
      #     Make sure the variable value is of the datatype you plan to send later
      attrib_rnd = await my_machine.add_variable(my_ua_namespace, "Random Number", 0)  #0 since this will be an int
      attrib_time = await my_machine.add_variable(my_ua_namespace, "Server Time", datetime.datetime.now()) #this will be a Time
      #     This attribute value can be written to by a client
      attrib_toggler = await my_machine.add_variable(my_ua_namespace, "Toggle Me", False) #false since this will be a bool
      await attrib_toggler.set_writable()
      attrib_runcontrol = await my_machine.add_variable(my_ua_namespace, "Server On", True) #false since this will be a bool
      await attrib_runcontrol.set_writable()

      # Add some attributes to my_machine_id, since these are static, we won't assign a variable
      await my_machine_id.add_variable(my_ua_namespace, "Manufacturer", "CESMII")  #this will be a string, per the spec
      await my_machine_id.add_variable(my_ua_namespace, "ManufacturerUri", "https://www.cesmii.org")  #this will be a string, per the spec
      await my_machine_id.add_variable(my_ua_namespace, "MonthOfConstruction", "5")  #this will be an int, per the spec
      await my_machine_id.add_variable(my_ua_namespace, "InitialOperationDate", datetime.datetime.now())  #this will be a Time, per the spec
      attrib_location = await my_machine_id.add_variable(my_ua_namespace, "Location", "Los Angeles, CA")  #this will be writeable and a string, per the spec
      await attrib_location.set_writable()

      # Create a Work Request
      workrequest_type = await my_ua_server.nodes.base_object_type.add_object_type(my_ua_namespace, "WorkRequestType")
      my_workrequest = await my_ua_server.nodes.objects.add_object(my_ua_namespace, "MyWorkRequest", workrequest_type.nodeid)
      await my_workrequest.add_variable(my_ua_namespace, "WorkRequestId", "Work Request 123")  #this will be a string, per the spec

      # Create a Job Order
      joborder_type = await my_ua_server.nodes.base_object_type.add_object_type(my_ua_namespace, "ISA95JobOrderDataType")
      my_joborder = await my_workrequest.add_object(my_ua_namespace, "MyJobOrder", joborder_type.nodeid)
      await my_joborder.add_variable(my_ua_namespace, "JobOrderID", "Job 123")  #this will be a string, per the spec
      await my_joborder.add_variable(my_ua_namespace, "JobOrderParameters", "An array of job-specific parameters goes here")  #in the spec, this is an array

      # Create Material
      material_type = await my_ua_server.nodes.base_object_type.add_object_type(my_ua_namespace, "ISA95MaterialDataType")
      my_material = await my_joborder.add_object(my_ua_namespace, "MaterialRequirements", material_type.nodeid)

      # Create a Glass Material Requirements Structure
      snode1, _ = await new_struct(my_ua_server, my_ua_namespace, "Glass", [
            new_struct_field("MaterialDefinitionID", ua.VariantType.UInt32),
            new_struct_field("Description", ua.VariantType.String),
            new_struct_field("Quantity", ua.VariantType.UInt32),
            new_struct_field("Properties", ua.VariantType.String, array=True),
      ])
      custom_objs = await my_ua_server.load_data_type_definitions()
      await my_material.add_variable(my_ua_namespace, "Glass", ua.Variant(ua.Glass(), ua.VariantType.ExtensionObject))

      # Create a Sash Material Requirements Object
      sash_material_type = await my_ua_server.nodes.base_object_type.add_object_type(my_ua_namespace, "ISA95MaterialSashDataType")
      my_material = await my_material.add_object(my_ua_namespace, "Sash", sash_material_type.nodeid)
      await my_material.add_variable(my_ua_namespace, "MaterialDefinitionId", "")
      await my_material.add_variable(my_ua_namespace, "Description", "")
      await my_material.add_variable(my_ua_namespace, "Quantity", "")
      await my_material.add_variable(my_ua_namespace, "NamedProperty1", "")
      await my_material.add_variable(my_ua_namespace, "NamedProperty2", "")

      print("Initalized AddressSpace!")

      try:
            print()
            print("Starting Simple OPC UA Server...")
            print()

            running = True
            async with my_ua_server:
                  while running == True:
                        #Update the attribute values for my object
                        new_rnd = random.randint(0,99)
                        new_time = datetime.datetime.now()
                        new_toggle = await attrib_toggler.get_value()
                        running = await attrib_runcontrol.get_value()
                        await attrib_rnd.set_value(new_rnd)
                        await attrib_time.set_value(new_time)

                        print ("Current values: ", new_rnd, new_time, new_toggle)

                        await asyncio.sleep(sample_rate)
      finally:
            await my_ua_server.stop()
            print("Server Shut Down")

if __name__ == "__main__":
    asyncio.run(main())