# Reference: https://www.youtube.com/watch?v=mEbPHflLNyc&list=PLWw98q-Xe7iGf-c4b6zF0bnJA9avEN_mF

from opcua import Server
from random import randint
import datetime
import RPi.GPIO as GPIO



import time


server = Server()

url = "opc.tcp://192.168.1.13:4840"

server.set_endpoint(url)

name = "OPCUA_SIMULATION_SERVER"

addspace = server.register_namespace(name)
print("Addspace :", addspace)

node = server.get_objects_node()

print("Node : ", node)

Param = node.add_object(addspace, "Parameters")

print("Parame :", Param)

var  = Param.add_variable(addspace, "VARIABLE", 10)
print("Variable is {}".format(var))
var.set_writable()

#server.start()

#print("Server Started at {}".format(url))

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.output(17, GPIO.LOW)  # make the output LOW level
print("GPIO output is set to LOW")

try:
    print("Start Server")
    server.start()
    print("Server Online")
    print("Server Started at {}".format(url))



    while True:
          t = var.get_value()
          print("Value is {}".format(t))

          if t == 1:
             GPIO.output(17, GPIO.HIGH)
             print("LED is ON")
          elif t == 0:
             GPIO.output(17, GPIO.LOW)
             print("LED is OFF")

          time.sleep(2)
finally:
    server.stop()
    print("Server Offline")


