import copy
import json
import logging
import os
import time

from aws_helper.helper import aws_provider, AwsHelper
from json_parser.exceptions import JsonParserException
from json_parser.vault_handler import Vault
from json_parser.wrappers import vault_provider

logger = logging.getLogger(__name__)


class JsonParser:
    valid_sub_categories = []
    my_sub_category = ""
    vault_handler: [Vault, None]
    vault_settings = {}
    aws_handler: [AwsHelper, None]
    aws_settings = {}
    data = {}
    valid_keys = []
    use_when = False

    def __setitem__(self, key, value):
        if key not in self.valid_keys:
            raise JsonParserException("Setitem failure", ("%s is not a valid key" % key))
        self.data[key] = value

    def __getitem__(self, key):
        if key not in self.valid_keys:
            raise JsonParserException("Getitem failure", ("%s is not a valid key" % key))
        if isinstance(self.data.get(key), dict):
            return self._parse_config(self.data.get(key))
        return self.data.get(key)

    def __init__(self, aws_region="", data=None, valid_keys=None, use_when=False, sub_categories=[], my_category=""):
        if aws_region:
            self.aws_settings = {"aws_region": aws_region}
        if valid_keys:
            self.valid_keys = valid_keys
        if use_when:
            self.use_when = use_when
        if data:
            self.data = data
        if sub_categories:
            self.valid_sub_categories = sub_categories
        if my_category:
            self.my_sub_category = my_category

        self.vault_handler = None
        self.aws_handler = None

    def load_data(self, data):
        self.data = data

    def _parse_value(self, data):
        if isinstance(data, dict):
            backend_provider = data.get("backend_provider", None)
            if backend_provider:
                backend_function = self._get_backend_data(backend_provider)
                return backend_function(data)
            return_data = {}
            for key, value in data.items():
                return_data[key] = self._parse_value(value)
            return return_data
        return data

    def _parse_config(self, config: dict):
        if not config:
            return {}
        if not self._when_run(config.get('when')):
            return {}

        return_data = copy.deepcopy(config)

        # Move any node-specific areas to the root
        for key, value in config.items():

            if key in self.valid_sub_categories:
                if key == self.my_sub_category:
                    for subkey, subvalue in value.items():
                        return_data[subkey] = subvalue
                del return_data[key]

        # find and get any "backend" data entries
        for rkey, rvalue in return_data.items():
            return_data[rkey] = self._parse_value(rvalue)

        return return_data

    def _get_backend_data(self, provider):
        if provider == "vault":
            return self._get_backend_data_vault
        elif provider == "parameter_store":
            return self._get_backend_data_paramstore
        elif provider == "file":
            return self._get_backend_data_file
        elif provider == "json_file":
            return self._get_backend_data_json_file
        elif provider == "environment":
            return self._get_backend_data_environment
        elif provider == "test":
            return self._get_backend_data_mock
        else:
            raise JsonParserException("Unknown provider",
                                      ("Unknown provider %s is not a valid data provider", provider))

    @staticmethod
    def _get_backend_data_mock(_):
        return "backend_data"

    @vault_provider
    def _get_backend_data_vault(self, config):
        path = config.get("vault_path")
        key = config.get("vault_key")
        if not path or not key:
            raise Exception("vault_path and vault_key are both required when pulling values from Vault")
        return self.vault_handler.get_kv(path)[key]

    @aws_provider
    def _get_backend_data_paramstore(self, config):
        attempt = 0
        max_attempts = 24

        while attempt < max_attempts:
            attempt += 1
            if self.aws_handler.get_parameter(config.get("path"), True):
                break
            time.sleep(5)

        return self.aws_handler.get_parameter(config.get("path"), True)['Parameter']['Value']

    @staticmethod
    def _get_backend_data_file(config):
        path = config.get("filename")
        if not path:
            raise JsonParserException("Minimum configuration for file is not provided",
                                      "filename is missing")

        try:
            with open(path, 'r') as f:
                content = f.read()
        except FileNotFoundError as err:
            raise JsonParserException("Could not open configfile", err)
        return content

    @staticmethod
    def _get_backend_data_json_file(config):
        path = config.get("filename")
        key = config.get("key")
        if not path or not key:
            raise JsonParserException("Minimum configuration for json file not provided",
                                      "filename or key are missing")
        try:
            with open(path, 'r') as f:
                values = json.loads(f.read())
        except FileNotFoundError as err:
            raise JsonParserException("Could not open json configfile", err)
        except (OSError, json.JSONDecodeError) as err:
            raise JsonParserException("Json config file contains invalid json", err)
        if not values.get(key):
            raise JsonParserException("Json config file does not contain expected key",
                                      ("key %s must exist in the config", key))
        return values[key]

    @staticmethod
    def _get_backend_data_environment(config):
        env_var = config.get("env_var")
        default = config.get("default", "")
        if not env_var:
            raise JsonParserException("Minimum configuration for environment variable not provided",
                                      "env_var is required")
        return os.getenv(env_var, default)

    def _when_run(self, config):
        if not self.use_when:
            return True
        if not config:
            return False
        if isinstance(config, list):
            if self.my_sub_category in config:
                return True
            return False
        if config in ['always', 'once']:
            return True
        return False
