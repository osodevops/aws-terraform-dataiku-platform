import botocore
import botocore.exceptions


class GlobalVariables:
    dss_client: object

    def __init__(self, dss_client):
        self.dss_client = dss_client

    def get_variables(self):
        return self.dss_client.get_variables()

    def set_variables(self, variables):
        try:
            print("Setting %s global variables." % (variables))
            self.dss_client.set_variables(variables)
        except botocore.exceptions.ClientError as err:
            print("Variables %s failed to update." % (variables))
            raise err
