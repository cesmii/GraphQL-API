import json
from smip import graphql
import requests

class fis_machine():
        def __init__(self):
                self.MachineId = None
                self.SmipId = None
        def __str__(self):
                return f"{self.MachineId},{self.SmipId}"
        def toJson(self):
                return json.dumps(self, default=lambda o: o.__dict__)
                
class utils:

        def __init__(self, authenticator, password, username, role, endpoint, verbose=True):
                self.smipgraphql = graphql(authenticator, password, username, role, endpoint, verbose)
                return
                
        def find_smip_equipment_of_type(self, typename):
                smp_query = f'''query get_machines {{
				        equipments(filter: 
                                                {{typeName: {{includesInsensitive: "{typename}"}}}}
                                        ) {{
                                                id
                                                displayName
                                        }}
				}}'''		
                smp_response = ""
                try:
                        smp_response = self.smipgraphql.post(smp_query)
                        equipments = smp_response['data']['equipments']
                        return equipments
                except requests.exceptions.HTTPError as e:
                        print("\033[31mAn error occured accessing the SM Platform:\033[0m")
                        print(e)
                        return[]

        def find_smip_equipment_of_parent(self, parentid):
                smp_query = f'''query get_stations {{
                                        equipments(filter: {{partOfId: {{equalTo: "{parentid}"}}}}) {{
                                                displayName
                                                id
                                                attributes {{
                                                        displayName
                                                        id
                                                }}
                                        }}
                                }}
                                '''		
                smp_response = ""
                try:
                        smp_response = self.smipgraphql.post(smp_query)
                        equipments = smp_response['data']['equipments']
                        return equipments
                except requests.exceptions.HTTPError as e:
                        print("\033[31mAn error occured accessing the SM Platform:\033[0m")
                        print(e)
                        return[]
        
        def find_smip_type_id(self, typename):
                smp_query = f'''query get_stations {{
                                        equipmentTypes(filter: {{relativeName: {{equalTo: "{typename}"}}}}) {{
                                                id
                                        }}
                                }}
                                '''		
                smp_response = ""
                try:
                        smp_response = self.smipgraphql.post(smp_query)
                        typeid = smp_response['data']['equipmentTypes'][0]['id']
                        return typeid
                except requests.exceptions.HTTPError as e:
                        print("\033[31mAn error occured accessing the SM Platform:\033[0m")
                        print(e)
                        return[]