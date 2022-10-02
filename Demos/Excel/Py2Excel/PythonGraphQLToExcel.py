#! /usr/bin/env python3

''' Dependenices to install via pip
      pip install requests 
      pip install pandas '''
import os, argparse, json, requests
import pandas as pd
from datetime import datetime
import config   #copy config-example.py to config.py and set values
from smip import graphql

# Allow Config overrides from command line
parser = argparse.ArgumentParser(description="GraphQL to Excel for the CESMII SMIP: A command line utility for querying SMIP attribute samples to a CSV file. Command line arguments override defaults specified in config.py")
parser.add_argument("-t", "--tags", type=str, default=str(config.smip["tagids"]), help="A comma seperated list of tag or attribute IDs to query from the SMIP")
parser.add_argument("-s", "--startTimeOffset", type=int, default=config.smip["startTimeOffset"], help="The minute offset from the current time to use as the start time for the query")
parser.add_argument("-e", "--endTimeOffset", type=int, default=config.smip["endTimeOffset"], help="The minute offset from the current time to use as the end time for the query")
parser.add_argument("-a", "--authenticator", type=str, default=config.smip["authenticator"], help="The name of the GraphQL authenticator to use to query the SMIP")
parser.add_argument("-p", "--password", type=str, default=config.smip["password"], help="The password for the GraphQL authenticator to use to query the SMIP")
parser.add_argument("-n", "--name", type=str, default=config.smip["name"], help="The username for the GraphQL authenticator to use to query the SMIP")
parser.add_argument("-r", "--role", type=str, default=config.smip["role"], help="The role name for the GraphQL authenticator to use to query the SMIP")
parser.add_argument("-u", "--url", type=str, default=config.smip["url"], help="The endpoint URL for the GraphQL query")
parser.add_argument("-o", "--outputFile", type=str, default=config.excel["outputFile"], help="The filename to use to write the CSV output. Environment variables will be expanded if present, and $datetime will be replaced with the current date and time")
parser.add_argument("-x", "--autoOpenExcel", type=str, default=config.excel["autoOpen"], help="Use any value that can be coerced to boolean to indicate whether or not to automatically open Excel when done building the output file")
parser.add_argument("-v", "--verbose", type=str, default=config.smip["verbose"], help="Use any value that can be coerced to a boolean true to run in verbose mode")
args = parser.parse_args()

# Setup SMIP Connection
graphql = graphql(config.smip["authenticator"], config.smip["password"], config.smip["name"], config.smip["role"], config.smip["url"], config.smip["barrer_token"])
#   Format Input
tags = args.tags.strip('][').split(', ')
tag_list = ""
for tag in tags: 
    tag_list += '"' + str(tag) + '",'
args.tags = tag_list
startTime=graphql.make_datetime_utc(args.startTimeOffset)   #TODO Support absolute DateTime input
endTime=graphql.make_datetime_utc(args.endTimeOffset)   #TODO Support absolute DateTime input

# Setup Excel Output
args.outputFile = os.path.expandvars(args.outputFile)
now = datetime.now()
dt_string = now.strftime("%Y-%m-%d-%H-%M-%S")
args.outputFile = args.outputFile.replace("$datetime", dt_string)
excel_command = os.path.expandvars(config.excel["excelCommand"])

# Main Program
def main():
    global current_bearer_token
    print("Requesting Data from CESMII Smart Manufacturing Platform...")
    print()

    smp_query = graphql.build_getRawHistoryDataWithSampling_query(args.tags, startTime, endTime)
    smp_response = ""

    try:
        smp_response = graphql.post(smp_query, bool(args.verbose))
    except requests.exceptions.HTTPError as e:
        print("An error occured accessing the SM Platform!")
        print(e)
 
    print()
    print ("Got a Query response from SMIP")

    if bool(args.verbose):
        print ("JSON Payload...")
        smp_response_formatted = json.dumps(smp_response, indent=2)
        print(smp_response_formatted)
        print()

    recs = smp_response['data']['getRawHistoryDataWithSampling']
    df1 = pd.json_normalize(recs)

    if bool(args.verbose):
        print ("CSV Normalized Data...")
        print(df1)
        print()

    # Output to excel
    #TODO Can we format the data better?
    df1.to_csv(args.outputFile, index=False)
    if bool(args.autoOpenExcel):
        if bool(args.verbose):
            print ("Opening Excel with command '" + excel_command + "', file '" + args.outputFile + "'")
        else:
            print ("Opening Excel file: " + args.outputFile)
        os.system(excel_command + " " + args.outputFile)
    else:
        print ("Excel data created as: " + args.outputFile)

    exit(0)

# Print some info
print()
print ("GraphQL to Excel for the CESMII SMIP - Python3 Version")
print ("======================================================")
print ("Querying " + " " + config.smip["url"] + " for tags " + args.tags)
print ("Using time range: " + startTime + " - " + endTime)
if bool(args.verbose):
    print ("Verbose mode: On")
print()

# Call main program
main()
