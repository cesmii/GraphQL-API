import json
from smip import graphql
from datetime import datetime
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

        def make_datetime_utc(self):
                utc_time = str(datetime.utcnow())
                time_parts = utc_time.split(" ")
                utc_time = "T".join(time_parts)
                time_parts = utc_time.split(".")
                utc_time = time_parts[0] + "Z"
                return utc_time
                
        def find_smip_equipment_of_type(self, typename):
                smp_query = f'''query get_machines {{
				        equipments(filter: 
                                                {{typeName: {{includesInsensitive: "{typename}"}}}}
                                        ) {{
                                                id
                                                relativeName
                                                displayName
                                        }}
				}}'''		
                smp_response = ""
                try:
                        smp_response = self.smipgraphql.post(smp_query)
                        equipments = smp_response['data']['equipments']
                        return equipments
                except requests.exceptions.HTTPError as e:
                        print("\033[31mAn error occured querying the SM Platform:\033[0m")
                        print(e)
                        return []

        def find_smip_equipment_of_parent(self, parentid):
                smp_query = f'''query get_stations {{
                                        equipments(filter: {{partOfId: {{equalTo: "{parentid}"}}}}) {{
                                                displayName
                                                relativeName
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
                        print("\033[31mAn error occured querying the SM Platform:\033[0m")
                        print(e)
                        return []
        
        def create_smip_equipment_of_typeid(self, parentid, typeid, equipmentname, internalname):
                smp_mutation = f'''
				mutation MyNewEquipmentMutation {{
				createEquipment(
					input: {{
						equipment: {{
                                                        displayName: "{equipmentname}"
                                                        relativeName: "{internalname}"
                                                        typeId: "{typeid}"
                                                        partOfId: "{parentid}"
						}}
					}}) {{
						equipment {{
							id
							displayName
						}}
					}}
				}}
				'''		
                smp_response = ""
                try:
                        smp_response = self.smipgraphql.post(smp_mutation)
                        equipmentid = smp_response['data']['createEquipment']['equipment']['id']
                        return equipmentid
                except requests.exceptions.HTTPError as e:
                        print("\033[31mAn error occured writing to the SM Platform:\033[0m")
                        print(e)
                        return None

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
                        print("\033[31mAn error occured querying the SM Platform:\033[0m")
                        print(e)
                        return None
        
        def find_attributes_of_equipment_id(self, equipmentid):
                smp_query = f'''query get_attributes {{
                                        equipment(id: "{equipmentid}") {{
                                                attributes {{
                                                        relativeName
                                                        id
                                                }}
                                        }}
                                }}
                                '''		
                smp_response = ""
                try:
                        smp_response = self.smipgraphql.post(smp_query)
                        attributes = smp_response['data']['equipment']['attributes']
                        return attributes
                except requests.exceptions.HTTPError as e:
                        print("\033[31mAn error occured querying the SM Platform:\033[0m")
                        print(e)
                        return None

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
                        smp_response = self.smipgraphql.post(smp_mutation)
                        data = smp_response['data']
                        return data
                except requests.exceptions.HTTPError as e:
                        print("\033[31mAn error occured writing to the SM Platform:\033[0m")
                        print(e)
                        return None