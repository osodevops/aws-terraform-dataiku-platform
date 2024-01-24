import logging
import os
import botocore.config

from exceptions import BackupException


class ConfigException(BackupException):
    pass


class Config:
    try:
        region = os.environ.get('REGION', 'eu-west-2')
        boto_config = botocore.config.Config(
            region_name=region,
            signature_version='v4',
            retries={
                'max_attempts': 4,
                'mode': 'standard'
            }
        )
        tag_application = os.environ.get('TAG_APPLICATION', 'Dataiku')
        tag_environment = os.environ.get('TAG_ENVIRONMENT', "")
        tag_deployment = os.environ.get('TAG_DEPLOYMENT', "")
        database_id = os.environ.get('DATABASE_ID', 'dataiku')
    except KeyError as err:
        raise ConfigException('Could not import all configuration values', err)

    log = logging.getLogger('backup-volume')
    log.setLevel(os.environ.get("LOG_LEVEL", "INFO"))
