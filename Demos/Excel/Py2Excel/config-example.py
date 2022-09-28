#!/usr/bin/env python
smip = {
    "verbose": 0,
    "authenticator": "myauthenticatorname",
    "password": "myauthenticatorspassword",
    "name": "myusername",
    "role": "myauthenticatorsrole",
    "url": "https://MYINSTANCE.cesmii.net/graphql",
    "barrer_token": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xl...",
    "tagids": [1033, 3137],
    "startTimeOffset": 10000,
    "endTimeOffset": 0
}
excel = {
    "autoOpen": 1,
    "outputFile": "%temp%\output-$datetime.csv",
    "excelCommand": "start EXCEL.EXE",
    "note:": "on a mac use open -a 'path/Microsoft Excel.app'"
}