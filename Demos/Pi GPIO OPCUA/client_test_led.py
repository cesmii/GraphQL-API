# Reference: https://www.youtube.com/watch?v=mEbPHflLNyc&list=PLWw98q-Xe7iGf-c4b6zF0bnJA9avEN_mF

from opcua import Client

import datetime
import time


url = "opc.tcp://192.168.1.13:4840"

client = Client(url)


try:

    client.connect()
    print("Client Connected")

    var = client.get_node("ns=2;i=2")

    print("Initial Value: {}".format(var.get_value()))

    var.set_value(1)

    while True:
       led_input = input ("Enter a number: 0 or 1 ")
       led_value = int(led_input)
       print ("The number you entered is: {}", led_value)
       var.set_value(led_value)

       time.sleep(4)

finally:
    client.close_session()
    print("Client Offline")




