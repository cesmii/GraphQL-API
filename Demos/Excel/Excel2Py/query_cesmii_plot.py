import numpy as np
import xlwings as xw
import pandas as pd
import datetime as dt
import argparse
import requests
import os
import json
import matplotlib.pyplot as plt

import cesmii_credentials # Credentials are read from this file

# What does this program do?
# This program demonstrates capability of executing GraphQL queries from Excel spreadsheet using Python
# 1. It first calls a CSV file to get the data into the Excel spreadsheet
# 2. It then calls GraphQL mutation to send the data to CESMII SM Platform based on the tagid
# 3. It then makes GraphQL query to receive the data from CESMII SM Platform based on the tagid
# 4. It also plots a graph using matplotlib

#Bearer token is available at  https://???.cesmii.net/api/graphql/?authorizationHeader=1
# If expired this code will automatically generate for you.
 
def main():
  read_data()
  
if __name__== "__main__":
  main()

current_bearer_token = "Bearer ey"

# GraphQL query expects data to be sent one column at a time. So get one column at a time and add a status column to it
def do_split(full_df, column_no):
    df_new = full_df.iloc[:,[0,column_no]].copy()
    df_new['status'] = pd.Series([1 for x in range(len(df_new.index))])
    df_new = df_new.astype(str)

    return df_new



parser = argparse.ArgumentParser()


authenticator_name=cesmii_credentials.authenticator_name
authenticator_passwd=cesmii_credentials.authenticator_passwd
user_name=cesmii_credentials.user_name
authenticator_role=cesmii_credentials.authenticator_role
instance_graphql_endpoint=cesmii_credentials.instance_graphql_endpoint

parser.add_argument("-a", "--authenticator", type=str, default=authenticator_name, help="Authenticator Name")
parser.add_argument("-p", "--password", type=str, default=authenticator_passwd, help="Authenticator Password")
parser.add_argument("-n", "--name", type=str, default=user_name, help="Authenticator Bound User Name")
parser.add_argument("-r", "--role", type=str, default=authenticator_role, help="Authenticator Role")
parser.add_argument("-u", "--url", type=str, default=instance_graphql_endpoint, help="GraphQL URL")


args = parser.parse_args(args=[])

def perform_graphql_request(content, url=args.url, headers=None):
  r = requests.post(url, headers=headers, data={"query": content})
  r.raise_for_status()
  return r.json()


def get_bearer_token (auth=args.authenticator, password=args.password, name=args.name, url=args.url, role=args.role):
  response = perform_graphql_request(f"""
    mutation authRequest {{
      authenticationRequest(
        input: {{authenticator: "{auth}", role: "{role}", userName: "{name}"}}
      ) {{
        jwtRequest {{
          challenge, message
        }}
      }}
    }}
  """)
  jwt_request = response['data']['authenticationRequest']['jwtRequest']
  if jwt_request['challenge'] is None:
      raise requests.exceptions.HTTPError(jwt_request['message'])
  else:
      print("Challenge received: " + jwt_request['challenge'])
      response=perform_graphql_request(f"""
        mutation authValidation {{
          authenticationValidation(
            input: {{authenticator: "{auth}", signedChallenge: "{jwt_request["challenge"]}|{password}"}}
            ) {{
            jwtClaim
          }}
        }}
    """)
  jwt_claim = response['data']['authenticationValidation']['jwtClaim']
  return f"Bearer {jwt_claim}"



def do_query(smp_query):
  global current_bearer_token
  print("Requesting Data from CESMII Smart Manufacturing Platform...")
  print()

  ''' Request some data -- this is an equipment query.
        Use Graphiql on your instance to experiment with additional queries
        Or find additional samples at https://github.com/cesmii/API/blob/main/Docs/queries.md '''
#  smp_query = """
#    {
#      equipments {
#        id
#        displayName
#      }
#    }"""
  smp_response = ""

  try:
    #Try to request data with the current bearer token
    smp_response = perform_graphql_request(smp_query, headers={"Authorization": current_bearer_token})
  except requests.exceptions.HTTPError as e:
    # 403 Client Error: Forbidden for url: https://demo.cesmii.net/graphql
    #print(e)
    if "forbidden" in str(e).lower() or "unauthorized" in str(e).lower():
      print("Bearer Token expired!")
      print("Attempting to retreive a new GraphQL Bearer Token...")
      print()

      #Authenticate
      current_bearer_token = get_bearer_token()

      print("New Token received: " + current_bearer_token)
      print()

      #Re-try our data request, using the updated bearer token
      # TODO: This is a short-cut -- if this subsequent request fails, we'll crash. You should do a better job :-)
      smp_response = perform_graphql_request(smp_query, headers={"Authorization": current_bearer_token})
    else:
      print("An error occured accessing the SM Platform!")
      print(e)
      exit(-1)

  return smp_response


def create_mutation_string(column_id, column_name, tagid, startTime, endTime, data_df):
    header = 'mutation { replaceTimeSeriesRange(input: {attributeOrTagId: "' + tagid +'" entries: '
    footer = ' startTime: "'+ startTime +'" endTime: "' + endTime + '" } ) { clientMutationId json } }'
    split_df=do_split(data_df,column_id)
    split_df.rename(columns={column_name:'value'},inplace=True)
    mutation_data=split_df.to_json(orient='records', lines=False).replace('"timestamp"', 'timestamp').replace('"value"','value').replace('"status"','status')
    mutation_data.replace('"value"','value')
    mutation_string = "{}{}{}".format(header, mutation_data, footer)
    return mutation_string


def create_query_string(tagid, startTime, endTime):
    query_string = '{ getRawHistoryDataWithSampling(maxSamples: 0, ids: ["'+ tagid + '"], startTime: "' +\
                     startTime +'",  endTime: "' + endTime + '"){ ts floatvalue} }'
    return query_string



def read_data():

    # reading csv file 
    # Caution Excel will expect the absolute (full) path of the input file.  So update it.
#    data_file='mutation_data.csv'
    data_file=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mutation_data.csv')
    data_df= pd.read_csv(data_file)

    data_df = data_df.astype(str)
    #print(data_df)
    wb = xw.Book.caller()
    ws1 = wb.sheets[0]
    ws1.clear_contents()

    wb.sheets[0].range('A1').value = data_df
    
#
#   Using GraphQL mutation to populate the data onto the CESMII SM Platform
#   Replace the tagid, startTime and endTime
#'

    startTime="2021-06-21"
    endTime="2021-07-24"
    names = ["current","potential","power"]
    tagIds = ["107927", "107928", "107929"]
    dfs = {}
    for i in range(len(names)):
      mutation_string = create_mutation_string(i+1, names[i], tagIds[i], startTime, endTime, data_df)
      # print(mutation_string + '\n')
      smp_response = do_query(str(mutation_string))
      # print("Response from SM Platform was...")
      # print(json.dumps(smp_response, indent=2))


#
#   Using GraphQL query to return the data from CESMII SM Platform
#   Replace the tagid, startTime and endTime
#
    startTime="2021-02-20 00:00:00+00"
    endTime="2021-07-25 00:12:00+00"
    for i in range(len(names)):
      smp_data_query = create_query_string(tagIds[i], startTime, endTime)
      #print(smp_data_query)
      smp_response = ""
      smp_response = do_query(smp_data_query)
      #print("Response from SM Platform was...")
      #print(json.dumps(smp_response, indent=2))

      recs = smp_response['data']['getRawHistoryDataWithSampling']
      dfs[i] = pd.json_normalize(recs)


    wb.sheets[0].range('A20').value = dfs[0]
    wb.sheets[0].range('A30').value = dfs[1]
    wb.sheets[0].range('A40').value = dfs[2]

    new_df = pd.concat([dfs[0], dfs[1]['floatvalue']], axis=1)
    read_df =  pd.concat([new_df, dfs[2]['floatvalue']], axis=1)
    read_df.columns = ['ts', 'current', 'potential', 'power']
    #new_df2
    wb.sheets[0].range('G20').value = read_df


    fig = plt.figure()
    plt.plot(read_df['current'], read_df['potential'])
    plt.xlabel('current')
    plt.ylabel('potential')
    wb.sheets[0].pictures.add(fig, name='MyPlot', update=True) 
