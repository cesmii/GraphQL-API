# Overview

This project is design to illustrate a progression from simple on-device data collection, adding a sensor, and experimenting with surfacing data through various approaches and protocols. It was used for a joint CESMII/MTConnect webinar in December, 2021.

# Hardware Used

+ Raspberry 3B+
+ Adafruit SI7021 Temperature and Humdity Sensor
+ Appropriate wires

# Software Required

**Python3**

**AdaFruit CircuitPython**
+ pip3 install adafruit-circuitpython-si7021
+ https://learn.adafruit.com/adafruit-si7021-temperature-plus-humidity-sensor/circuitpython-code

**Flask**
+ https://flask.palletsprojects.com/en/2.0.x/quickstart/

**smbus**
+ apt-get install python-smbus python3-smbus python-dev python3-dev i2c-tools
+ pip3 install smbus2

**opcua**
+ apt-get install libxslt-dev
+ pip3 install opcua

**paho-mqtt**
+ pip3 install paho-mqtt
