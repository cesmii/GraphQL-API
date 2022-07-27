import time, sys, random
import config
from pylogix import PLC
import paho.mqtt.client as paho

broker=config.mqtt["broker"]
port=config.mqtt["port"]

sample_rate = config.cip["samplerate"]
do_toggle = config.toggler["toggle"]
toggle_at = config.toggler["every"]
use_toggle_at = toggle_at
last_toggle = False

def on_publish(client, userdata, result):
        print("MQTT Topic Updated!")
        pass

client1= paho.Client("cesmii_demo")
client1.on_publish = on_publish

print ("Updating MQTT Broker at " + str(broker) + " with light value every " + str(sample_rate) + " seconds")
if do_toggle:
        if toggle_at == -1:
                print ("Light will be toggled randomly")
        else:
                print ("Light will be toggled every " + str(toggle_at) + " samples")

with PLC() as comm:
        comm.IPAddress = config.cip["plc"]
        comm.Micro800 = True
        loop_count = 0
        last_toggle = comm.Read('_IO_EM_DO_01').Value
        while True:
                # read the value of the switch
                ret = comm.Read('_IO_EM_DO_01')
                print("\nLight on:", ret.Value)

                # send the value to the broker as a yellow light topic
                client1.connect(broker,port)
                mt= client1.publish("light/yellow",int(ret.Value))
                
                # toggle the value if requested
                if do_toggle:
                        loop_count += 1
                        if loop_count >= use_toggle_at:
                                loop_count = 0
                                if toggle_at == -1:
                                        use_toggle_at = random.randint(2, 20)
                                last_toggle = not last_toggle
                                ret = comm.Write('Demo_Switch', last_toggle)
                                print("Set new light value:", ret.Value, ret.Status)

                # wait until next sample
                time.sleep(sample_rate)
