import logging
import os
import botocore.config

from exceptions import VolumeException
from dynamic_config import DynamicConfig


def string_to_bool(data):
    if data in ['False', 'false', 'F', 'f', False]:
        return False
    return True


class Config:
    def __init__(self):
        try:
            dynamic_config = DynamicConfig("/opt/volume-manager/dynamic-settings.json")

            region = dynamic_config.get('region')

            # Volume settings
            self.encrypt_volumes = string_to_bool(dynamic_config.get('encrypt_volumes'))
            self.volume_iops = dynamic_config.get('volume_iops')
            self.kms_key = dynamic_config.get('kms_key')
            self.volume_type = dynamic_config.get('volume_type')
            self.volume_size = dynamic_config.get('volume_size')
            self.volume_device_name = dynamic_config.get('volume_device_name')
            self.volume_mount_point = dynamic_config.get('volume_mount_point')

            self.boto_config = botocore.config.Config(
                region_name=region,
                signature_version='v4',
                retries={
                    'max_attempts': 4,
                    'mode': 'standard'
                }
            )
        except KeyError as err:
            raise VolumeException('Could not import all configuration values', err)

        logging.basicConfig(level=os.environ.get('LOG_LEVEL', 'INFO'))
        self.log = logging.getLogger(__name__)
        self.log.setLevel(logging.INFO)
        logging.getLogger("botocore").setLevel(logging.WARNING)
