import json
import logging
import subprocess

import dataikuapi

import wrappers

logger = logging.getLogger(__name__)


class ApiTest:
    dss_client: [dataikuapi.DSSClient, None]
    apideployer_client: [dataikuapi.dss.apideployer.DSSAPIDeployer, None]
    dss_auth_settings: dict

    @wrappers.dss_client
    @wrappers.apideployer_client
    def __init__(self, dss_auth_settings):
        self.dss_auth_settings = dss_auth_settings


def api_main():
    token = ""
    try:
        dsscli_output = subprocess.run(
            f"su - dataiku -c '/data/dataiku/bin/dsscli api-keys-list --output json --no-header'",
            shell=True,
            check=True, capture_output=True)
        for key in json.loads(dsscli_output.stdout.decode()):
            if key['admin'] is True:
                token = key['key']
            break
    except subprocess.CalledProcessError as err:
        logger.critical(f"Error: Could not get the api keys via dsscli: {err.output}")
    except (KeyError, json.JSONDecodeError):
        logger.critical(f"Error: Could read Json key response")

    dss_auth_settings = {
        "url": "http://localhost:11200",
        "api_key": token,
        "user": 'admin'
    }

    api_test = ApiTest(dss_auth_settings=dss_auth_settings)

    # API non-functional calls
    try:
        print("Cluster API")
        cluster = api_test.dss_client.create_cluster("api_test")
        cluster.get_status()
        api_test.dss_client.list_clusters()
        print("OK")

        print("Plugin API")
        api_test.dss_client.list_plugins()
        res = api_test.dss_client.install_plugin_from_store("eks-clusters")
        res.wait_for_result()
        plugin = api_test.dss_client.get_plugin("eks-clusters")
        plugin.get_settings()
        print("OK")

        print("General settings API")
        settings = api_test.dss_client.get_general_settings()
        settings.save()
        print("OK")

        print("Connections API")
        api_test.dss_client.create_connection("api_test", "EC2", {}, "ALLOWED", [])
        api_test.dss_client.list_connections()
        print("OK")

        print("API-deployer API")
        api_client = api_test.dss_client.get_apideployer()
        api_client.list_stages()
        api_client.list_infras()
        print("OK")

        # print success string
        print("API TEST SUCCESS")

    except Exception as err:
        print(f"API TEST FAILED: {err}")


if __name__ == "__main__":
    # execute only if run as a script
    api_main()
    