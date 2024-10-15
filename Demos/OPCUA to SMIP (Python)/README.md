## Overview
This project reads tags from an OPC UA server, and writes their values to SMIP attributes.

### How to run
- Copy `config_example.py` > `config.py`
- Replace the contents of `config.py` with SMIP authenticator information, OPC UA Endpoint, and the name of the taglist file
```
smip = dict(
    authenticator = "AUTHENTICATOR",
    password = "PASSWORD",
    username = "USERNAME",
    role = "ROLE",
    endpoint = "https://SMIP_INSTANCE.cesmii.net/graphql", 
    verbose = False
)
opcua = dict(
    endpoint = "OPC_UA_ENDPOINT",
    taglist_file = "TAGLIST_WITH_NODEIDS",
    sample_rate = 2 #number of seconds
)
MAX_TRIES = 5
```
- Update or create a new taglist file that contains information for each tag: attribute (or tag) name, OPC UA Node ID to read from, SMIP Attribute ID to write to. Note: The data types for the SMIP attributes should be created to match the OPC UA Tag Data Type
```
{
    "attribute":"TAG_NAME1",
    "smip_attr_id":"123456",
    "opcua_nodeid":"ns=2;s=/Node/Path/To/Tag"
}
```
- run `python read-and-send.py`
