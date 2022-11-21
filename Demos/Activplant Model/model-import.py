import datetime, time, random
import config
import argparse
import smiputils
import requests
import random
import json
from enum import Enum

class NodeTypes(Enum):
        NodeGroup = 1
        Node = 2

# Load config and args
parser = argparse.ArgumentParser()
parser.add_argument("-smip", "--smip", type=int, default=False)
args = parser.parse_args()
verbose = config.smip["verbose"]
use_smip = False

# Remember important info once discovered
smip_group_ids = {}
node_type_ids = {}

def debug(verbose, message, sleep=0):
        if verbose:
                print (message)
        if sleep:
                time.sleep(sleep)

#Show config
print("\nCESMII Activplant Importer")
print("==========================")
debug(verbose, "Verbose mode: on")
if bool(args.smip):
        print("\033[36mCESMII SMIP publishing enabled at: " + config.smip["url"] + "\033[0m")
        use_smip = True
print("Using Activplant Endpoint: " + str(config.php["endpoint"]))

# Read in Activplant model from PHP endpoint
url = config.php["endpoint"]
username = config.php["username"]
password = config.php["password"]
response = requests.get(url, auth=(username, password))
time.sleep(config.smip["throttle_rate"])
if (response.status_code == 200):
        data = response.json()
        print("Connected to database: " + data['databaseName'])
        print("Groups Found: " + str(data['groupCount']))
        print("Assets Found: " + str(data['assetCount']))
        print("")

# Setup SMIP Connection
if use_smip:
        sm_utils = smiputils.utils(config.smip["authenticator"], config.smip["password"], config.smip["name"], config.smip["role"], config.smip["url"], verbose)

def showAddNodeWithType(thisNode, nodeType, indent, lastGroupParentId):
        spaces = ' '
        global node_type_ids
        global smip_group_ids
        node_type_id = ""

        if nodeType == NodeTypes.NodeGroup:
                node_int_name = "vpng_" + str(thisNode['groupId'])
                node_name = str(thisNode['groupName']).replace("\n", " ")
        else:
                node_int_name = "vpng_" + str(thisNode['nodeId'])
                node_name = str(thisNode['nodeName']).replace("\n", " ")
        print((indent * spaces) + "[" + str(nodeType) + ": " + node_name + "]")

        if use_smip:
                parent_group_int_name = "vpng_" + str(lastGroupParentId)        # Only groups can be parents
                # Check if this equipment already exists in smip:
                found_node = None
                smip_nodes = sm_utils.find_smip_equipment_of_type(config.smip["type_ids"][str(nodeType)])

                for node in smip_nodes:    # if it exists, use it
                        if node_int_name == node["relativeName"]:
                                found_node = node["id"]
                if found_node == None: # if it doesn't exist, create it
                        if nodeType in node_type_ids.keys():
                                node_type_id = node_type_ids[str(nodeType)]
                        else:
                                node_type_ids[str(nodeType)] = sm_utils.find_smip_type_id(config.smip["type_ids"][str(nodeType)])
                                node_type_id = node_type_ids[str(nodeType)]

                        use_parent_id = config.smip["parent_equipment_id"]
                        if parent_group_int_name in smip_group_ids.keys():      #TODO: If resuming an interupted run, parents will be unknown
                                use_parent_id = smip_group_ids[parent_group_int_name]

                        print ((indent * spaces) + "\033[36mAdd new " + str(nodeType).replace("NodeTypes.", "") + " to SMIP: " + node_name + " (" + str(node_int_name) + ") for parent: " + parent_group_int_name + " (" + str(use_parent_id) + ").\033[0m")

                        found_node = sm_utils.create_smip_equipment_of_typeid(use_parent_id, node_type_id, node_name, node_int_name)
                        smip_group_ids[node_int_name] = found_node
                        debug (verbose, "New Node ID: " +  found_node)
                        debug (verbose, json.dumps(smip_group_ids))
        if "groupChildren" in thisNode.keys():  #if this node has children, keep recursing
                recurseNodes(thisNode['groupChildren'], indent, lastGroupParentId)

def recurseNodes(nodes, indent, lastGroupParentId):
        for key in nodes:
                time.sleep(config.smip["throttle_rate"])
                if isinstance(nodes[key], dict):
                        if "parentId" in nodes[key]:
                                if nodes[key]['parentId'] != lastGroupParentId:
                                        lastGroupParentId = nodes[key]['parentId']
                                        indent = indent + 1
                        if "type" in nodes[key]:
                                if nodes[key]['type'] == "NodeGroup":
                                        showAddNodeWithType(nodes[key], NodeTypes.NodeGroup, indent, lastGroupParentId)
                                if nodes[key]['type'] == "Node":
                                        showAddNodeWithType(nodes[key], NodeTypes.Node, indent, lastGroupParentId)

recurseNodes(data['equipmentModel'], 2, None)