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
        deployed_path = self['dss'].get('deployment_path')
        user = self["dss"].get('admin_user')

        if not self["dss"].get('admin_key'):
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
            self.data["dss"]["admin_key"] = token

    def initialize_backend_settings(self):
        self.vault_settings = {
            "vault_role": self['dss'].get('vault_role'),
            "vault_endpoint":  self['dss'].get('vault_endpoint'),
            "vault_skip_tls": self['dss'].get('vault_skip_tls'),
            "vault_path": self['dss'].get('vault_auth_path'),
            "vault_os_nonce_path": self['dss'].get('vault_os_nonce_path'),
            "vault_mock_endpoint": self['dss'].get('vault_mock_endpoint'),
            "vault_auth_method": self['dss'].get('vault_auth_method'),
            "vault_auth_token": self['dss'].get('vault_auth_token')
        }