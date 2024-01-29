import json
import logging
import subprocess

from json_parser import JsonParser

logger = logging.getLogger(__name__)


class Config(JsonParser):
    valid_keys = [
        'auth_token_source', 'endpoint_url', 'installation_directory', 'pre_prod_alb_automation_dns_name',
        'prod_alb_automation_dns_name', 'deployment', 'set_user_profile', 'set_admin_password', 'update_license',
        'install_ini_settings', 'configure_rds', 'plugins', 'eks_cluster', 'containerized_execution',
        'cgroups', 's3_connections', 'api_infrastructure', 'project_infrastructures', 'populate_ssh_keys',
        'global_variables', 'saml', 'dss'
    ]

    def get_dss_auth_settings(self):
        data = self.data["dss"]
        deployed_path = data['deployment_path']
        user = data['admin_user']

        if not data["admin_key"]:
            token = ""
            try:
                dsscli_output = subprocess.run(
                    f"su - dataiku -c '{deployed_path}/bin/dsscli api-keys-list --output json --no-header'",
                    shell=True,
                    check=True, capture_output=True)
                for key in json.loads(dsscli_output.stdout.decode()):
                    if key[user] is True:
                        token = key['key']
                    break
            except subprocess.CalledProcessError as err:
                logger.critical(f"Error: Could not get the api keys via dsscli: {err.output}")
            except (KeyError, json.JSONDecodeError):
                logger.critical(f"Error: Could read Json key response")
            self.data["dss_auth"]["admin_key"] = token

    def initialize_backend_settings(self):
        self.vault_settings = {
            "vault_role": self.data['dss'].get('vault_role'),
            "vault_endpoint":  self.data['dss'].get('vault_endpoint'),
            "vault_skip_tls": self.data['dss'].get('vault_skip_tls'),
            "vault_path": self.data['dss'].get('vault_path'),
            "vault_os_nonce_path": self.data['dss'].get('vault_os_nonce_path'),
            "vault_mock": self.data['dss'].get('vault_mock')
        }