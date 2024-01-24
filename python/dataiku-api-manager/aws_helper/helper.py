import json
import logging

import boto3
import botocore

import botocore.exceptions
import botocore.config

from exceptions import AwsHelperException

logger = logging.getLogger(__name__)


def ec2_client_wrapper(func):
    def wrapper(self, *args, **kwargs):
        if not self.ec2_client:
            self.ec2_client = boto3.client('ec2', config=self.boto_config)
        result = func(self, *args, **kwargs)
        return result
    return wrapper


def ssm_client_wrapper(func):
    def wrapper(self, *args, **kwargs):
        if not self.ssm_client:
            self.ssm_client = boto3.client('ssm', config=self.boto_config)
        result = func(self, *args, **kwargs)
        return result
    return wrapper


def lb_client_wrapper(func):
    def wrapper(self, *args, **kwargs):
        if not self.lb_client:
            self.lb_client = boto3.client('elbv2', config=self.boto_config)
        result = func(self, *args, **kwargs)
        return result
    return wrapper


def s3_client_wrapper(func):
    def wrapper(self, *args, **kwargs):
        if not self.s3_client:
            self.s3_client = boto3.client('s3', config=self.boto_config)
        result = func(self, *args, **kwargs)
        return result
    return wrapper


def aws_provider(func):
    def wrapper(self, *args, **kwargs):
        if not self.aws_handler:
            logger.info(f"Configuring AWS connection")
            if not self.aws_settings.get('aws_region:'):
                self.aws_settings['aws_region'] = requests.get('http://169.254.169.254/latest/meta-data/placement/availability-zone').text[:-1]
            self.aws_handler = AwsHelper(
                boto_config=botocore.config.Config(
                    region_name=self.aws_settings['aws_region'],
                    signature_version='v4',
                    retries={
                        'max_attempts': 4,
                        'mode': 'standard'
                    }
                )
            )
        return func(self, *args, **kwargs)
    return wrapper


class AwsHelper:
    ssm_client: [boto3.client, None] = None
    lb_client: [boto3.client, None] = None
    ec2_client: [boto3.client, None] = None
    s3_client: [boto3.client, None] = None
    boto_config: [dict, None] = None

    def __init__(self, boto_config=None):
        self.boto_config = boto_config
        if not boto_config:
            self.boto_config = botocore.config.Config(
                region_name='eu-west-2',
                signature_version='v4',
                retries={
                    'max_attempts': 4,
                    'mode': 'standard'
                }
            )

    @ec2_client_wrapper
    @ssm_client_wrapper
    @lb_client_wrapper
    def get_clients(self):
        return

    @ec2_client_wrapper
    def get_instance_id(self, config: dict = None):
        # config = {
        #     'states': ['running'],
        #     'additional_tags': {"key": "value"},
        #     'exclude_id': "abc123"
        # }
        if not config:
            raise AwsHelperException("get_instance_id called incorrectly",
                                     "requires a config object")

        filter_tags = [
            {
                'Name': 'instance-state-name',
                'Values': config.get('states')
            }
        ]

        for tag_key, tag_value in config.get('additional_tags', {}).items():
            if tag_value:
                filter_tags.append({
                    'Name': f"tag:{tag_key}",
                    'Values': [tag_value]
                })

        instance = self.ec2_client.describe_instances(
            Filters=filter_tags,
            MaxResults=10
        )
        try:
            for result in instance['Reservations'][0]['Instances']:
                if result['InstanceId'] != config.get('exclude_id'):
                    return result['InstanceId']
        except (AttributeError, IndexError):
            return None

    @ec2_client_wrapper
    def get_az_from_instance(self, instance_id):
        instance = self.ec2_client.describe_instances(
            InstanceIds=[
                instance_id,
            ]
        )
        return instance['Reservations'][0]['Instances'][0]['Placement']['AvailabilityZone']

    @ec2_client_wrapper
    def get_instance_tags(self, instance_id):
        instance = self.ec2_client.describe_instances(
            InstanceIds=[
                instance_id,
            ]
        )
        return instance['Reservations'][0]['Instances'][0]['Tags']

    @ssm_client_wrapper
    def get_parameter(self, param, decrypt=False):
        parameter = False
        try:
            parameter = self.ssm_client.get_parameter(
                Name=param,
                WithDecryption=decrypt
            )

        except botocore.exceptions.ClientError as err:
            if err.response['Error']['Code'] == 'ParameterNotFound':
                print(f"{param} not found")
                return parameter
            raise err

        return parameter

    @ssm_client_wrapper
    def create_or_update_parameter(self, config: dict = None):
        # config = {
        #     'param': "something",
        #     'value': "something",
        #     'type': "SecureString",
        #     'overwrite': True
        # }
        if not config:
            raise AwsHelperException("create_or_update_parameter called incorrectly",
                                     "requires a config object")

        try:
            parameter = self.ssm_client.put_parameter(
                Name=config.get('param'),
                Value=config.get('value'),
                Type=config.get('type'),
                Overwrite=config.get('overwrite')
            )
            print(f"Parameter created/updated {config.get('param')}")
        except botocore.exceptions.ClientError as err:
            logger.critical(f"Paramstore {config.get('param')} was not updated. ")
            raise err

        return parameter

    @lb_client_wrapper
    def get_load_balancers(self):
        try:
            lb = self.lb_client.describe_load_balancers()
        except botocore.exceptions.ClientError as err:
            logger.critical(f"Load Balancer not found. ")
            raise err

        return lb
        
    def get_load_balancer_by_name(self, name):
        lb = self.get_load_balancers()
        alb = [val for val in lb['LoadBalancers'] if val['LoadBalancerName'] == name]

        return alb

    def get_snapshot_data(self, snapshot_id="", search_tags={}):
        filter_tags = []

        for tag_key, tag_value in search_tags.items():
            if tag_value:
                filter_tags.append({
                    'Name': f"tag:{tag_key}",
                    'Values': [tag_value]
                })
        parameters = {
            'Filters': filter_tags
        }

        if snapshot_id:
            parameters['SnapshotIds'] = [snapshot_id]
        else:
            parameters['MaxResults'] = 100

        logger.debug(f"Getting snapshot with parameters: {parameters}")
        try:
            response = self.ec2_client.describe_snapshots(**parameters)
        except botocore.exceptions.ClientError:
            return None

        if not response['Snapshots']:
            return None

        logger.debug(f"Got response {response}")
        return response

    @ec2_client_wrapper
    def get_volume_data(self, config: dict = None):
        # config = {
        #     'az': 'eu-west-1',
        #     'volume_id': 'abc123',
        #     'search_tags': 'abc123',
        # }
        if not config:
            raise AwsHelperException("get_volume_data called incorrectly",
                                     "requires a config object")

        filter_tags = [
            {
                'Name': 'availability-zone',
                'Values': [config.get('az')]
            },
        ]

        for tag_key, tag_value in config.get('search_tags', {}).items():
            if tag_value:
                filter_tags.append({
                    'Name': f"tag:{tag_key}",
                    'Values': [tag_value]
                })

        parameters = {
            'Filters': filter_tags
        }

        if config.get('volume_id'):
            parameters['VolumeIds'] = [config.get('volume_id')]
        else:
            parameters['MaxResults'] = 100

        logger.debug(f"Getting volume with parameters: {parameters}")

        try:
            response = self.ec2_client.describe_volumes(**parameters)
        except botocore.exceptions.ClientError:
            return None

        if not response['Volumes']:
            return None

        logger.debug(f"Got response {response}")
        return response

    @ec2_client_wrapper
    def delete_volume(self, volume_id):
        try:
            response = self.ec2_client.delete_volume(VolumeId=volume_id)
            return response
        except botocore.exceptions.ClientError as err:
            logger.warning(f"Failed to remove old volume: {err.response['Error']['Message']}")

    @ec2_client_wrapper
    def create_volume_from_snapshot(self, config: dict = None):
        # config = {
        #     'az': 'eu-west-1',
        #     'snapshot_id': 'abc123',
        #     'instance_id': 'abc123',
        #     'tags': {'key': 'value'},
        #     'volume_type': 'gp3',
        #     'volume_size': '150',
        #     'encrypt_volumes': True,
        #     'kms_key': 'abc123',
        #     'volume_iops': '1050'
        # }
        if not config:
            raise AwsHelperException("create_volume_from_snapshot called incorrectly", "requires a config object")

        tag_set = [
            {
                'Key': 'Instance',
                'Value': config.get('instance_id')
            },
            {
                'Key': 'Snapshot',
                'Value': "true"
            }
        ]
        for tag_key, tag_value in config.get('tags', {}).items():
            if tag_value:
                tag_set.append({
                    'Key': tag_key,
                    'Value': tag_value
                })

        parameters = {
            'AvailabilityZone': config.get('az'),
            'SnapshotId': config.get('snapshot_id'),
            'VolumeType': config.get('volume_type'),
            'Size': int(config.get('volume_size')),
            'TagSpecifications': [
                {
                    'ResourceType': 'volume',
                    'Tags': tag_set
                }
            ]
        }

        if config.get('encrypt_volumes'):
            parameters['Encrypted'] = config.get('encrypt_volumes')
            if config.get('kms_key'):
                parameters['KmsKeyId'] = config.get('kms_key')

        if config.get('volume_iops'):
            parameters['Iops'] = int(config.get('volume_iops'))

        logger.debug(f"Getting snapshot with parameters: {parameters}")
        response = self.ec2_client.create_volume(**parameters)

        logger.debug(f"Got response {response}")
        return response['VolumeId']

    @ec2_client_wrapper
    def create_blank_volume(self, config: dict = None):
        # config = {
        #     'az': 'eu-west-1',
        #     'instance_id': 'abc123',
        #     'tags': {'key': 'value'}
        # }
        if not config:
            raise AwsHelperException("create_blank_volume called incorrectly", "requires a config object")

        tag_set = [
            {
                'Key': 'Instance',
                'Value': config.get('instance_id')
            },
            {
                'Key': 'Snapshot',
                'Value': "true"
            }
        ]
        for tag_key, tag_value in config.get('tags', {}).items():
            if tag_value:
                tag_set.append({
                    'Key': tag_key,
                    'Value': tag_value
                })

        parameters = {
            'AvailabilityZone': config.get('az'),
            'Size': int(config.get('volume_size')),
            'VolumeType': config.get('volume_type'),
            'TagSpecifications': [
                {
                    'ResourceType': 'volume',
                    'Tags': tag_set
                }
            ]
        }

        if config.get('encrypt_volumes'):
            parameters['Encrypted'] = config.get('encrypt_volumes')
            parameters['KmsKeyId'] = config.get('kms_key')

        if config.get('volume_iops'):
            parameters['Iops'] = int(config.get('volume_iops'))

        logger.debug(f"Getting snapshot with parameters: {parameters}")
        response = self.ec2_client.create_volume(**parameters)

        logger.debug(f"Got response {response}")
        return response['VolumeId']

    @ec2_client_wrapper
    def attach_volume(self, config: dict = None):
        # config = {
        #     'instance_id': 'abc123',
        #     'volume_id': 'abc123',
        #     'volume_device_name': '/dev/sda2'
        # }
        if not config:
            raise AwsHelperException("attach_volume called incorrectly", "requires a config object")

        response = self.ec2_client.attach_volume(
            Device=config.get('volume_device_name'),
            InstanceId=config.get('instance_id'),
            VolumeId=config.get('volume_id')
        )

    @s3_client_wrapper
    def get_file_from_s3(self, config: dict = None):
        # config = {
        #     'bucket_name': 'abc123',
        #     'key': 'abc123',
        # }
        if not config:
            raise AwsHelperException("get_file_from_s3 called incorrectly", "requires a config object")

        response = self.s3_client.get_object(
            Bucket=config.get('bucket_name'),
            Key=config.get('key')
        )

        data = json.loads(response['Body'].read())
        response['Body'].close()

        return data
