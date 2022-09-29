import argparse
import requests
import json
import time
import string

class graphql:

    def __init__(self, authenticator, password, username, role, endpoint, verbose=True):
        self.current_bearer_token = ""
        self.parser = None
        self.args = None
        self.verbose = verbose

        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-smip", "--smip", type=int, default=True)    # this is only here for outer wrapper
        self.parser.add_argument("-a", "--authenticator", type=str, default=authenticator)
        self.parser.add_argument("-p", "--password", type=str, default=password)
        self.parser.add_argument("-n", "--name", type=str, default=username)
        self.parser.add_argument("-r", "--role", type=str, default=role)
        self.parser.add_argument("-u", "--url", type=str, default=endpoint)
        self.args = self.parser.parse_args()
    
    def clean_whitespace(self, thestring):
        return " ".join(thestring.strip().split())

    def post(self, content):
        if self.current_bearer_token == "":
            self.current_bearer_token = self.get_bearer_token()
        try:
            response = self.perform_graphql_request(content)
        except requests.exceptions.HTTPError as e:
            if "forbidden" in str(e).lower() or "unauthorized" in str(e).lower():
                print ("\033[36mNot authorized, getting new token...\033[0m")
                self.current_bearer_token = self.get_bearer_token()
                response = self.perform_graphql_request(content)
            else:
                print("\033[31mFatal: An unhandled error occured accessing the SM Platform!\033[0m")
                print(e)
                raise requests.exceptions.HTTPError(e)
        return response

    def perform_graphql_request(self, content, auth=False):
        if self.verbose:
            print()
            print("\033[36mPosting request with content: \033[0m")
            print(self.clean_whitespace(content))
        if auth == True:
            header=None
        else:
            header={"Authorization": self.current_bearer_token}
        r = requests.post(self.args.url, headers=header, data={"query": content})
        r.raise_for_status()
        if self.verbose:
            print("\033[36mGot response: \033[0m" + json.dumps(r.json()).encode('utf-8').decode('unicode-escape'))
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
        if jwt_request['challenge'] is None:
            print ("No challenge in response")
            raise requests.exceptions.HTTPError(jwt_request['message'])
        else:
            if self.verbose:
                print("\033[36mAuth challenge received: " + jwt_request['challenge'] + "\033[0m")
            else:
                print("\033[36mAuthorizing with the SMIP\033[0m")

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