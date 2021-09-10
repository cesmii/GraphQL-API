#!/usr/bin/env python
mqtt = {
    "broker": "lab.cesmii.net",
    "clientprefix": "CESMII-Sim-"
}
smip = {
    "authenticator": "cesmiidemoapp",
    "password": "cesmii",
    "name": "cesmiihq",
    "role": "demo_owner",
    "url": "https://demo.cesmii.net/graphql"
}


tank_amount = 5
tank_name_prefix = "mytank"
tanks_relations = [[i+1] for i in range(tank_amount-1)] + [[]]
tanks_relations[1] = [2, 3]
tanks_relations[2] = [4]
tanks_sizes= [20 for i in range(tank_amount)]
tanks_sizes[2] = 10
tanks_sizes[3] = 10
tanks_fill_level = [0 for i in range(tank_amount)]
cavitations = [False for i in range(tank_amount)]
leaks = [False for i in range(tank_amount)]
#cavitations[1] = True
#cavitations[2] = True
#leaks[1] = True



one_tank_size = 20

