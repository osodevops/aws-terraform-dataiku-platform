# https://doc.dataiku.com/dss/latest/python-api/client.html?highlight=create_connection#dataikuapi.DSSClient.create_connection


class Connection:
    dss_client: object

    def __init__(self, dss_client):
        self.dss_client = dss_client

    def create(self, name="", connection_type="", params={}, usable_by="", allowed_groups=[]):
        # Check connection already exists.
        if self.connected(name):
            return print("Connection %s settings already exist." % (name))

        self.dss_client.create_connection(name, connection_type, params, usable_by, allowed_groups)
        # Check the connection settings were added successfully.
        if self.connected(name):
            return print("Connection %s settings successfully added.." % (name))
        else:
            raise Exception("Connection %s settings failed to add." % (name))

    def list(self):
        return self.dss_client.list_connections()

    def connected(self, name):
        try:
            return self.dss_client.list_connections()[name]
        except KeyError:
            return False