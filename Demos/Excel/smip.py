import argparse
import requests
import json
from datetime import timezone
import datetime

class graphql:

    def __init__(self, authenticator, password, username, role, endpoint, barrer_token):
        self.current_bearer_token = barrer_token
        self.authenticator = authenticator
        self.password = password
        self.username = username
        self.role = role
        self.endpoint = endpoint

    def post(self, content, verbose):
        if self.current_bearer_token == "":
            self.current_bearer_token = self.get_bearer_token(verbose)
        try:
            response = self.perform_graphql_request(content, verbose)
        except requests.exceptions.HTTPError as e:
            if "forbidden" in str(e).lower() or "unauthorized" in str(e).lower():
                print ("Not authorized, getting new token...")
                self.current_bearer_token = self.get_bearer_token(verbose)
                response = self.perform_graphql_request(content, verbose)
            else:
                print("An unhandled error occured accessing the SM Platform!")
                print(e)
                raise requests.exceptions.HTTPError(e)
        return response

    def build_getRawHistoryDataWithSampling_query(self, tagids, startTime, endTime):
        query_string = '{ getRawHistoryDataWithSampling(maxSamples: 0, ids: ['+ tagids +\
            '], startTime: "' + startTime +\
            '",  endTime: "' + endTime + '"){ id ts floatvalue} }'
        return query_string

    def perform_graphql_request(self, content, verbose, auth=False):
        if verbose:
            print("Performing request with content: ")
            print(content)
            print()

        if auth == True:
            header=None
        else:
            header={"Authorization": self.current_bearer_token}
        r = requests.post(self.endpoint, headers=header, data={"query": content})
        r.raise_for_status()
        return r.json()
        
    def get_bearer_token (self, verbose):
        print ("Authenticating with Platform security")
        response = self.perform_graphql_request(f"""
        mutation authRequest {{
                authenticationRequest(
                    input: {{authenticator: "{self.authenticator}", role: "{self.role}", userName: "{self.username}"}}
                ) {{
                    jwtRequest {{
                    challenge, message
                    }}
                }}
                }}
            """, verbose, True) 
        jwt_request = response['data']['authenticationRequest']['jwtRequest']
        print ("Got an Auth request response from SMIP")
        if jwt_request['challenge'] is None:
            print ("No challenge in response")
            raise requests.exceptions.HTTPError(jwt_request['message'])
        else:
            print("Responding to Challenge: " + jwt_request['challenge'])
            response=self.perform_graphql_request(f"""
                mutation authValidation {{
                authenticationValidation(
                    input: {{authenticator: "{self.authenticator}", signedChallenge: "{jwt_request["challenge"]}|{self.password}"}}
                    ) {{
                    jwtClaim
                }}
                }}
            """, verbose, True)
        jwt_claim = response['data']['authenticationValidation']['jwtClaim']
        return f"Bearer {jwt_claim}"

    def make_datetime_utc(self, offset_minutes, endTime=datetime.datetime.now):
        utc_time = endTime(timezone.utc)
        time_delta = datetime.timedelta(minutes=offset_minutes)
        utc_time = utc_time - time_delta
        str_time = str(utc_time)
        time_parts = str_time.split(" ")
        str_time = "T".join(time_parts)
        time_parts = str_time.split(".")
        str_time = time_parts[0] + "Z"
        return str_time
