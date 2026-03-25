from smip_client import SMIPClient


class SMIPMethods:
    """Higher-level SMIP operations (wraps a `SMIPClient`).

    Keep transport/auth in `SMIPClient` and GraphQL operations here so the
    client file can be reused as a template.
    """
    def __init__(self, client: SMIPClient):
        self.client = client

    def get_equipment(self):
        """Return equipments { id displayName }"""
        query = '{ equipments { id displayName } }'
        return self.client.query(query)


__all__ = ['SMIPMethods']
