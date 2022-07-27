#!/usr/bin/env python

cip = {
    "plc": "192.168.50.240",
    "samplerate": 2
}

smip = {
    "authenticator": "AUTHENTICATOR",
    "password": "PASSWORD",
    "name": "NAME",
    "role": "ROLE",
    "url": "INSTANCE_ENDPOINT"
}

mqtt = {
    "broker": "192.168.50.125",
    "port": 1883
}

toggler = {
    "toggle": True,
    # set to -1 for randomized toggle
    "every": 2  
}