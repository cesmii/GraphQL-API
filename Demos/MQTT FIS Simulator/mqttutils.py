import json
from smip import graphql
import requests
               
class utils:

        def __init__():
            return
        
        def make_json_payload(curr_data, simulation_keys):
            # TODO: I built the JSON payload as a string because I got tired of fighting with Python's dicts, but this should be object-based
            payload_data = "{\n"
            for i in range(len(simulation_keys)):
                    payload_data += "\t\"" + simulation_keys[i] + "\":"
                    payload_data += "\"" + str(curr_data[i]) + "\""
                    if i < len(simulation_keys) - 1:
                            payload_data += ",\n"
                    else:
                            payload_data += "\n}"
            return payload_data