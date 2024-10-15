import argparse
import requests
import json
from datetime import datetime, timezone

verbose = False
class graphql:
    def __init__(self, authenticator, password, username, role, endpoint):
        self.current_bearer_token = ""
        self.parser = None
        self.args = None

        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-a", "--authenticator", type=str, default=authenticator)
        self.parser.add_argument("-p", "--password", type=str, default=password)
        self.parser.add_argument("-n", "--name", type=str, default=username)
        self.parser.add_argument("-r", "--role", type=str, default=role)
        self.parser.add_argument("-u", "--url", type=str, default=endpoint)
        self.args = self.parser.parse_args()
    
    def print_verbose(self, string=""):
        if verbose is True:
            print(string)

    def post(self, content):
        if self.current_bearer_token == "":
            self.current_bearer_token = self.get_bearer_token()
        try:
            response = self.perform_graphql_request(content)
        except requests.exceptions.HTTPError as e:
            if "forbidden" in str(e).lower() or "unauthorized" in str(e).lower():
                self.print_verbose("Not authorized, getting new token...")
                self.current_bearer_token = self.get_bearer_token()
                response = self.perform_graphql_request(content)
            else:
                self.print_verbose("An unhandled error occured accessing the SM Platform!")
                self.print_verbose(e)
                raise requests.exceptions.HTTPError(e)
        return response

    def perform_graphql_request(self, content, auth=False):
        self.print_verbose("Performing request with content: ")
        self.print_verbose(content)
        self.print_verbose()
        if auth == True:
            header=None
        else:
            header={"Authorization": self.current_bearer_token}
        r = requests.post(self.args.url, headers=header, data={"query": content})
        r.raise_for_status()
        return r.json()
        
    def get_bearer_token (self):
        response = self.perform_graphql_request(f"""
        mutation authRequest {{
                authenticationRequest(
                    input: {{authenticator: "{self.args.authenticator}", role: "{self.args.role}", userName: "{self.args.name}"}}
                ) {{
                    jwtRequest {{
                    challenge, message
                    }}
                }}
                }}
            """, True) 
        jwt_request = response['data']['authenticationRequest']['jwtRequest']
        self.print_verbose("got auth request response")
        if jwt_request['challenge'] is None:
            self.print_verbose("no challenge in response")
            raise requests.exceptions.HTTPError(jwt_request['message'])
        else:
            self.print_verbose("Challenge received: " + jwt_request['challenge'])
            response=self.perform_graphql_request(f"""
                mutation authValidation {{
                authenticationValidation(
                    input: {{authenticator: "{self.args.authenticator}", signedChallenge: "{jwt_request["challenge"]}|{self.args.password}"}}
                    ) {{
                    jwtClaim
                }}
                }}
            """, True)
        jwt_claim = response['data']['authenticationValidation']['jwtClaim']
        return f"Bearer {jwt_claim}"

    def make_datetime_utc(self):
        return datetime.now(timezone.utc).replace(tzinfo=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ') 

    def build_alias_ts_mutation(self, ordinal, attributOrTagId, value):
        timestamp = self.make_datetime_utc()
        smp_mutation = f'''ts{ordinal}: replaceTimeSeriesRange (
                                input: {{
                                        entries: [
                                                {{ status: "0", timestamp: "{timestamp}", value: "{value}" }}
                                        ]
                                        attributeOrTagId: "{attributOrTagId}"
                                }}) {{
                                        json
                                }}
                                '''
        return smp_mutation

    def multi_tsmutate_aliases(self, aliasmutations):
            smp_mutation = f'''mutation tsmulti {{
                                    {aliasmutations}
                            }}
                            '''		
            smp_response = ""
            try:
                    smp_response = self.post(smp_mutation)
                    if 'errors' in smp_response:
                            print("\033[31mAn error occured writing to the SM Platform:\033[0m")
                            print(smp_response['errors'])
            except requests.exceptions.HTTPError as e:
                    print("\033[31mAn error occured writing to the SM Platform:\033[0m")
                    print(e)