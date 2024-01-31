import json
import logging
import sys

logger = logging.getLogger(__name__)


class DynamicConfig:
    config: dict
    defaults: dict

    def __init__(self, filename):
        # Set some common defaults
        self.defaults = {
            "region": "eu-west-2",
            "encrypt_volumes": False,
            "volume_iops": "",
            "kms_key": "",
            "volume_type": "gp3",
            "volume_size": 40,
            "volume_device_name": "/dev/xvdb",
            "volume_mount_point": "/data"
        }
        try:
            with open(filename, 'r') as f:
                file_values = json.loads(f.read())
        except FileNotFoundError:
            logger.critical("configuration file has not been deployed. Ending run")
            sys.exit(1)
        except (OSError, json.JSONDecodeError) as err:
            logger.critical(f"Could not open/read the dynamic configuration file: {err}")
            sys.exit(1)

        self.config = {**self.defaults, **file_values}

    def get(self, key):
        value = self.config.get(key, None)
        if value is None:
            logger.critical(f"Error getting dynamic config item {key}")
            sys.exit(1)

        return value
