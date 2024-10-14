#!/usr/bin/env python
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