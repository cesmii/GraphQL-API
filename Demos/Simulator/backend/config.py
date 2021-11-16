#!/usr/bin/env python
mqtt = {
    "broker": "mqtt.cesmii.net",
    "clientprefix": "CESMII-JWSim-"
}
smip = {
    "authenticator": "cesmiidemoapp",
    "password": "cesmii",
    "name": "cesmiihq",
    "role": "sandbox_group",
    "url": "https://sandbox.cesmii.net/graphql"
}


type_id = "37024"
parent_id = "37039"
tank_amount = 5
tank_name_prefix = "Tank "
tanks_relations = [[i+1] for i in range(tank_amount-1)] + [[]]
tanks_relations[1] = [2, 3]
tanks_relations[2] = [4]
tanks_sizes= [20 for i in range(tank_amount)]
tanks_sizes[2] = 10
tanks_sizes[3] = 10
tanks_fill_level = [0 for i in range(tank_amount)]
cavitations = [False for i in range(tank_amount)]
leaks = [False for i in range(tank_amount)]
cavitations[1] = False
#cavitations[2] = True
#leaks[1] = True
one_tank_size = 20
