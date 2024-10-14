# Reference: https://www.youtube.com/watch?v=mEbPHflLNyc&list=PLWw98q-Xe7iGf-c4b6zF0bnJA9avEN_mF

from opcua import Client
from smip import graphql
import config
import json
import time
import sys

graphql = graphql(config.smip["authenticator"], config.smip["password"], config.smip["username"], config.smip["role"], config.smip["endpoint"])

def read_tags_from_file(filename):
    with open(filename) as json_data:
        d = json.load(json_data)
        json_data.close()
        return d

def run_connector():
    client = Client(config.opcua["endpoint"])
    client.connect()
    graphql.print_verbose("OPC UA Client Connected")

    taglist = read_tags_from_file(config.opcua["taglist_file"])

    for tag in taglist:
        tag["node"] = client.get_node(tag["opcua_nodeid"])

    while True:
        try:
            # Read the values on the OPC UA server for each specified node
            alias_mutates = ""
            for tag in taglist:
                value = tag["node"].get_value()
                alias_mutates += graphql.build_alias_ts_mutation(tag["attribute"], tag["smip_attr_id"], value)
            # Send Query
            graphql.multi_tsmutate_aliases(alias_mutates)
            time.sleep(2)
        except (KeyboardInterrupt, SystemExit):
            print('\nKeyboardinterrupt caught')
            print('\n...Program Stopped Manually!')
            return 1
        except Exception as inst:
            print(type(inst))    # the exception type
            print(inst.args)     # arguments stored in .args
            print(inst)      
            client.disconnect()
            print("OPC UA Client Offline")
            return 1

def main():
    print("Running script to read data from {0} to {1}".format(config.opcua["endpoint"], config.smip["endpoint"]))

    tries = 0
    while tries < config.MAX_TRIES:
        print("Number of tries is {}".format(str(tries)))
        tries += run_connector()

    print("Max retries of connector reached")
    sys.exit(0)

if __name__ == '__main__':
    main()