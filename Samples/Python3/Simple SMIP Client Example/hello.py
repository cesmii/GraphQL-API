import json
from smip_client import SMIPClient
from smip_methods import SMIPMethods


def main():
    client = SMIPClient()

    # Test method on the client
    libs = client.get_libraries()
    print('--- libraries ---')
    print(json.dumps(libs, indent=2))

    # Methods class (keeps higher-level operations out of the client)
    methods = SMIPMethods(client)
    eq = methods.get_equipment()
    print('--- equipments ---')
    print(json.dumps(eq, indent=2))


if __name__ == '__main__':
    main()
