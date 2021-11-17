#!/usr/bin/env python
mqtt = {
    "broker": "BROKER_NAME",
    "clientprefix": "CLIENT_PREFIX"
}
smip = {
    "authenticator": "AUTHENTICATOR",
    "password": "PASSWORD",
    "name": "NAME",
    "role": "ROLE",
    "url": "INSTANCE_ENDPOINT"
}


type_id = "TYPE_ID"
parent_id = "PARENT_ID"
tank_amount = 5 #set your amount
tank_name_prefix = "Tank "
tanks_relations = [[i+1] for i in range(tank_amount-1)] + [[]]
#tanks_relations[1] = [2, 3]
#tanks_relations[2] = [4]
tanks_sizes= [20 for i in range(tank_amount)]
#tanks_sizes[2] = 10
#tanks_sizes[3] = 10
tanks_fill_level = [0 for i in range(tank_amount)]
cavitations = [False for i in range(tank_amount)]
leaks = [False for i in range(tank_amount)]

#you could set cavitation or leak for specific tank like following
#cavitations[2] = True
#leaks[1] = True
