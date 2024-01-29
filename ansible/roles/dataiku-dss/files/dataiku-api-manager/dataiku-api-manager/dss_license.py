class License:
    client: object

    def __init__(self, client):
        self.client = client

    def update(self, license_value):
        self.client.set_license(license_value)

    def check_status(self):
        license_info = self.client.get_licensing_status()['base']

        if license_info['expired']:
            raise Exception("Error: This license has expired")
        if not license_info['hasLicense'] or not license_info['valid']:
            raise Exception("Error: The license content is not valid. Installation is unlicensed")
