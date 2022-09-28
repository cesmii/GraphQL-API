#!/usr/bin/env python

# See: https://github.com/cesmii/API/blob/main/Docs/jwt.md
smip = {
    "authenticator": "YOUR_AUTHENTICATOR_NAME",
    "password": "AUTHENTICATOR_PASSWORD",
    "name": "AUTHENTICATOR_USERNAME",
    "role": "AUTHENTICATOR_ROLE",
    "url": "INSTANCE_ENDPOINT",
    "machine_type": "fis_machine",
    "station_type": "fis_station",
    "verbose": False
}

mqtt = {
    "broker": "broker",
    "port": 1883,
    "payload_topic_root": ""
}

simulator = {
    "event_sample_min": 3,
    "event_sample_max": 4,
    "data_file": "FISEvents.csv",
    "wait_between_machines": 3,
    "max_machines": 10,
    "num_stations_per_machine": 4
}