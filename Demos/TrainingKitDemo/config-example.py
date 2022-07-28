#!/usr/bin/env python

cip = {
    "plc": "192.168.50.240",
    "samplerate": 2
}

# See: https://github.com/cesmii/API/blob/main/Docs/jwt.md
smip = {
    "authenticator": "YOUR_AUTHENTICATOR_NAME",
    "password": "AUTHENTICATOR_PASSWORD",
    "name": "AUTHENTICATOR_USERNAME",
    "role": "AUTHENTICATOR_ROLE",
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