import logging

from json_parser.vault_handler import Vault

logger = logging.getLogger(__name__)


def string_to_bool(data):
    if data in ['False', 'false', 'F', 'f', False, None]:
        return False
    return True


def vault_provider(func):
    def wrapper(self, *args, **kwargs):
        if not self.vault_handler:
            logger.info(f"Logging in to Hashicorp Vault")
            self.vault_handler = Vault(
                role=self.vault_settings.get('vault_role'),
                endpoint=self.vault_settings.get('vault_endpoint'),
                skip_tls=string_to_bool(self.vault_settings.get('vault_skip_tls')),
                path=self.vault_settings.get('vault_path'),
                nonce_path=self.vault_settings.get('vault_nonce_path'),
                mock=string_to_bool(self.vault_settings.get('vault_mock_endpoint')),
                method=self.vault_settings.get('vault_auth_method')
            )
            self.vault_handler.login()
        return func(self, *args, **kwargs)
    return wrapper
