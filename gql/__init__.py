# Stub gql package for testing – provides a minimal Client class and gql helper.

class Client:
    def __init__(self, *args, **kwargs):
        pass

    async def execute_async(self, *args, **kwargs):
        # Return empty dict for any query – tests don't depend on real data.
        return {}
