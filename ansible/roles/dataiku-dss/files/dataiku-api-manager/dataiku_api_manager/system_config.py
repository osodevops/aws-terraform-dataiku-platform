import json
import logging
import os

import requests

from aws_helper import AwsHelper, aws_provider
from src import wrappers

logger = logging.getLogger(__name__)


class SystemConfig:
    aws_handler: [AwsHelper, None]
    aws_settings: dict
    system_json_file: str
    dss_config_file: str
    dss_config_s3_bucket: str
    dss_config_s3_key: str
    dss_config_s3_bucket_tag: str
    dss_config_s3_key_tag: str
    node_type: str
    dss_node_type_tag: str
    instance_id: str
    tags: dict

    def __init__(self, aws_region="", system_json_file="", dss_config_file="", dss_config_s3_bucket="",
                 dss_config_s3_key="", dss_config_s3_bucket_tag="", dss_config_s3_key_tag="", node_type="",
                 dss_node_type_tag=""):
        # Precedence: highest first
        self.aws_settings = {"aws_region": aws_region}
        self.aws_handler = None
        self.dss_config_file = dss_config_file
        self.dss_config_file = dss_config_file
        self.dss_config_s3_bucket_tag = dss_config_s3_bucket_tag
        self.dss_config_s3_key_tag = dss_config_s3_key_tag
        self.dss_config_s3_bucket = dss_config_s3_bucket
        self.dss_config_s3_key = dss_config_s3_key
        self.dss_node_type_tag = dss_node_type_tag
        self.node_type = node_type
        self.system_json_file = system_json_file
        self.instance_id = ""
        self.tags = {}

    @aws_provider
    def _get_instance_tag(self, search_tag, default):
        if not self.tags:
            if not self.instance_id:
                self.instance_id = requests.get('http://169.254.169.254/latest/meta-data/instance-id').text
            self.tags = self.aws_handler.get_instance_tags(self.instance_id)
        return self.tags.get(search_tag, default)

    @aws_provider
    def _get_bucket_data(self):
        return self.aws_handler.get_file_from_s3(
            {'bucket_name': self.dss_config_s3_bucket, 'key': self.dss_config_s3_key})

    def load_system_config(self):
        if self.system_json_file:
            with open(self.system_json_file, 'r') as f:
                data = json.loads(f.read())
            for key, value in data.items():
                if key in ['aws_settings', 'node_type', 'dss_config_file', 'dss_config_s3_bucket', 'dss_config_s3_key',
                           'dss_config_s3_bucket_tag', 'dss_config_s3_key_tag', 'dss_node_type_tag']:
                    if not getattr(self, key):
                        setattr(self, key, value)
                else:
                    logger.critical(f"System config file contained invalid key: {key}")

    def get_config_data(self):
        # Tag settings will override any value already given for a specific item
        if self.dss_config_file:
            with open(self.dss_config_file, 'r') as f:
                return json.loads(f.read())

        if self.dss_config_s3_key_tag:
            self.dss_config_s3_key = self._get_instance_tag(tag=self.dss_config_s3_key_tag,
                                                            default=os.getenv("S3_CONFIG_KEY"))

        if self.dss_config_s3_bucket_tag:
            self.dss_config_s3_bucket = self._get_instance_tag(tag=self.dss_config_s3_bucket_tag,
                                                               default=os.getenv("S3_CONFIG_BUCKET"))

        if self.dss_node_type_tag:
            self.node_type = self._get_instance_tag(tag=self.dss_node_type_tag,
                                                    default=os.getenv("DSSNODE_TYPE"))

        if self.dss_config_s3_key and self.dss_config_s3_bucket:
            return self._get_bucket_data()
