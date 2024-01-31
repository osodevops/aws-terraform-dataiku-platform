import logging

import boto3
import botocore

from config import Config

logger = logging.getLogger(__name__)


class Aws:
    ec2_client: boto3.client
    sts_client: boto3.client

    account: str
    config: Config

    def __init__(self, config: Config):
        self.config = config
        self.ec2_client = boto3.client('ec2', config=self.config.boto_config)
        self.sts_client = boto3.client('sts', config=self.config.boto_config)
        self.account = self.sts_client.get_caller_identity()['Account']

    def get_instance_id(self, states: list = [], additional_tags: dict = {}, exclude_id: str = ""):
        filter_tags = [
            {
                'Name': 'instance-state-name',
                'Values': states
            }
        ]

        for tag_key, tag_value in additional_tags.items():
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
                if result['InstanceId'] != exclude_id:
                    return result['InstanceId']
        except (AttributeError, IndexError):
            return None

    def get_az_from_instance(self, instance_id):
        instance = self.ec2_client.describe_instances(
            InstanceIds=[
                instance_id,
            ]
        )
        return instance['Reservations'][0]['Instances'][0]['Placement']['AvailabilityZone']

    def get_instance_tags(self, instance_id):
        instance = self.ec2_client.describe_instances(
            InstanceIds=[
                instance_id,
            ]
        )
        return instance['Reservations'][0]['Instances'][0]['Tags']

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

    def get_volume_data(self, az, volume_id="", snapshot_id="", search_tags={}):
        filter_tags = [
            {
                'Name': 'availability-zone',
                'Values': [az]
            },
        ]
        if snapshot_id:
            filter_tags.append({
                'Name': "snapshot-id",
                'Values': [snapshot_id]
            })

        for tag_key, tag_value in search_tags.items():
            if tag_value:
                filter_tags.append({
                    'Name': f"tag:{tag_key}",
                    'Values': [tag_value]
                })

        parameters = {
            'Filters': filter_tags
        }

        if volume_id:
            parameters['VolumeIds'] = [volume_id]
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

    def delete_volume(self, volume_id):
        try:
            response = self.ec2_client.delete_volume(VolumeId=volume_id)
            return response
        except botocore.exceptions.ClientError as err:
            logger.warning("Failed to remove old volume.")

    def set_common_params(self, instance_id, tags, az):
        tag_set = [
            {
                'Key': 'Instance',
                'Value': instance_id
            },
            {
                'Key': 'Snapshot',
                'Value': "true"
            }
        ]
        for tag_key, tag_value in tags.items():
            if tag_value:
                tag_set.append({
                    'Key': tag_key,
                    'Value': tag_value
                })

        parameters = {
            'AvailabilityZone': az,
            'VolumeType': self.config.volume_type,
            'Size': int(self.config.volume_size),
            'TagSpecifications': [
                {
                    'ResourceType': 'volume',
                    'Tags': tag_set
                }
            ]
        }

        if self.config.encrypt_volumes:
            parameters['Encrypted'] = self.config.encrypt_volumes
            if self.config.kms_key:
                parameters['KmsKeyId'] = self.config.kms_key

        if self.config.volume_iops:
            parameters['Iops'] = int(self.config.volume_iops)

        return parameters

    def create_volume_from_snapshot(self, az, snapshot_id, instance_id, tags):
        parameters = self.set_common_params(instance_id, tags, az)
        parameters['SnapshotId'] = snapshot_id

        logger.debug(f"Getting snapshot with parameters: {parameters}")
        response = self.ec2_client.create_volume(**parameters)

        logger.debug(f"Got response {response}")
        return response['VolumeId']

    def create_blank_volume(self, az, instance_id, tags):
        parameters = self.set_common_params(instance_id, tags, az)

        logger.debug(f"Getting snapshot with parameters: {parameters}")
        response = self.ec2_client.create_volume(**parameters)

        logger.debug(f"Got response {response}")
        return response['VolumeId']

    def attach_volume(self, instance_id, volume_id):
        response = self.ec2_client.attach_volume(
            Device=self.config.volume_device_name,
            InstanceId=instance_id,
            VolumeId=volume_id
        )

    def match_volume_attachment(self, instance_id, tag_set):
        instance = self.ec2_client.describe_instances(
            InstanceIds=[
                instance_id,
            ]
        )
        for volume in instance['Reservations'][0]['Instances'][0]['BlockDeviceMappings']:
            data = \
            self.get_volume_data(az=self.az, volume_id=volume['Ebs']['VolumeId'], search_tags=tag_set)['Volumes'][0]
            if data.get('Attachments', False):
                if data['Attachments'][0]['State'] in ['attaching', 'attached']:
                    return True
        return False
