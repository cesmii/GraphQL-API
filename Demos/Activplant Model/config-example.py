#!/usr/bin/env python

# See: https://github.com/cesmii/API/blob/main/Docs/jwt.md
smip = {
    "authenticator": "YOUR_AUTHENTICATOR_NAME",
    "password": "AUTHENTICATOR_PASSWORD",
    "name": "AUTHENTICATOR_USERNAME",
    "role": "AUTHENTICATOR_ROLE",
    "url": "INSTANCE_ENDPOINT",
    "asset_type": "vp_asset",
    "group_type": "vp_group",
    "type_ids": {
        "NodeTypes.Node": "vp_asset",
        "NodeTypes.NodeGroup": "vp_group"
    },
    "fed_id": "07",
    "parent_equipment_id": "28889",
    "verbose": False,
    "throttle_rate": 1
}

# You can also pass a specific DB in the querystring, like:
# https://YOURACTIVPLANTSERVER/ENDPOINT.PHP?dbname=YOUR_DATABASE_NAME
php = {
    "endpoint": "https://YOURACTIVPLANTSERVER/ENDPOINT.PHP",
    "username": "cesmii",
    "password": "YOURWEBPASSWORD"
}