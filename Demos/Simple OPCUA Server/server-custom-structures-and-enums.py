import logging
import asyncio

from asyncua import ua, Server
from asyncua.common.structures104 import new_struct, new_enum, new_struct_field

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger('asyncua')


async def main():
    # setup our server
    server = Server()
    await server.init()
    server.set_endpoint('opc.tcp://0.0.0.0:4840/freeopcua/server/')

    # setup our own namespace, not really necessary but should as spec
    uri = 'http://examples.freeopcua.github.io'
    idx = await server.register_namespace(uri)

    snode1, _ = await new_struct(server, idx, "MyStruct", [
        new_struct_field("MyBool", ua.VariantType.Boolean),
        new_struct_field("MyUInt32List", ua.VariantType.UInt32, array=True),
    ])

    custom_objs = await server.load_data_type_definitions()
#    print("Custom objects on server")
#    for name, obj in custom_objs.items():
#        print("    ", obj)

    await server.nodes.objects.add_variable(idx, "my_struct", ua.Variant(ua.MyStruct(), ua.VariantType.ExtensionObject))
#    await server.export_xml([server.nodes.objects, server.nodes.root, snode1, valnode], "structs_and_enum.xml")

    async with server:
        while True:
            await asyncio.sleep(1)


if __name__ == '__main__':
    asyncio.run(main())
