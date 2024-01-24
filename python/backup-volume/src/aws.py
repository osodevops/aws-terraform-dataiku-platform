from datetime import datetime

import boto3
import botocore.exceptions

from config import Config


class Aws:
    ec2_client: boto3.client
    sts_client: boto3.client
    rds_client: boto3.client
    cloudwatch_client: boto3.client

    def __init__(self):
        self.ec2_client = boto3.client('ec2', config=Config.boto_config)
        self.sts_client = boto3.client('sts', config=Config.boto_config)
        self.rds_client = boto3.client('rds', config=Config.boto_config)
        self.cloudwatch_client = boto3.client('cloudwatch', config=Config.boto_config)

    def raise_cloudwatch_alert(self):
        response = self.cloudwatch_client.put_metric_data(
            Namespace='Dataiku/',
            MetricData=[
                {
                    'MetricName': 'DataikuDSSUnexpectedLambdaFailure',
                    'Dimensions': [
                        {
                            'Name': 'Environment',
                            'Value': Config.tag_environment
                        },
                        {
                            'Name': 'Deployment',
                            'Value': Config.tag_deployment
                        }
                    ],
                    'Value': 1
                }
            ]
        )

    def get_az_from_instance(self, instance_id):
        try:
            instance = self.ec2_client.describe_instances(
                InstanceIds=[
                    instance_id,
                ]
            )

        except botocore.exceptions.ClientError as err:
            Config.log.critical(f"Could not find availability zone for instance {instance_id}. ")
            raise err

        return instance['Reservations'][0]['Instances'][0]['Placement']['AvailabilityZone']

    def get_snapshot_data(self, snapshot_id="", additional_tags={}):
        filter_tags = []
        for tag_key, tag_value in additional_tags.items():
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

        try:
            Config.log.debug(f"Getting snapshot with parameters: {parameters}")
            response = self.ec2_client.describe_snapshots(**parameters)

        except botocore.exceptions.ClientError as err:
            Config.log.critical("Could not find snapshot.")
            raise err

        if not response['Snapshots']:
            Config.log.warning('Did not find any snapshots matching criteria')

        Config.log.debug(f"Got response {response}")
        return response

    def get_volume_data(self, az, volume_id="", instance_id="", additional_tags={}):
        Config.log.debug(f"Got az {az}, volume_id {volume_id}, instance id {instance_id} tags {additional_tags}")
        filters = [{
                    'Name': 'availability-zone',
                    'Values': [az]
                }]

        if instance_id:
            filters.append({
                'Name': 'tag:Instance',
                'Values': [instance_id]
            })

        for tag_key, tag_value in additional_tags.items():
            if tag_value:
                filters.append({
                    'Name': f"tag:{tag_key}",
                    'Values': [tag_value]
                })

        parameters = {
            'Filters': filters
        }
        Config.log.debug(f"Final filters {filters}")

        if volume_id:
            parameters['VolumeIds'] = [volume_id]
        else:
            parameters['MaxResults'] = 100

        try:
            Config.log.debug(f"Getting volume with parameters: {parameters}")
            response = self.ec2_client.describe_volumes(**parameters)
        except botocore.exceptions.ClientError as err:
            Config.log.critical("Could not find volume.")
            raise err

        if not response['Volumes']:
            Config.log.info('Did not find any volumes matching criteria')

        Config.log.info(f"Got response {response}")
        return response

    def get_instance(self, instance_id):
        try:
            instance = self.ec2_client.describe_instances(
                InstanceIds=[
                    instance_id,
                ]
            )
        except botocore.exceptions.ClientError as err:
            Config.log.critical("Could not find instance.")
            raise err
        return instance['Reservations'][0]['Instances'][0]

    def get_instance_tags(self, instance_id):
        instance_data = self.get_instance(instance_id)
        tags = {}
        for tag in instance_data.get('Tags'):
            tags[tag['Key']] = tag['Value']
        return tags

    def create_snapshot(self, volume_id, additional_tags={"Application": "Dataiku-DSS"}):
        tags = []
        for tag_key, tag_value in additional_tags.items():
            if tag_value:
                tags.append({
                    'Key': tag_key,
                    'Value': tag_value
                })

        try:
            response = self.ec2_client.create_snapshot(
                Description='Backup of Dataiku data volume',
                VolumeId=volume_id,
                TagSpecifications=[
                    {
                        'ResourceType': 'snapshot',
                        'Tags': tags
                    }
                ]
            )
        except botocore.exceptions.ClientError as err:
            Config.log.critical("Could not create snapshot.")
            raise err

        return response['SnapshotId']

    def delete_volume(self, volume_id):
        try:
            response = self.ec2_client.delete_volume(VolumeId=volume_id)
            return response
        except botocore.exceptions.ClientError as err:
            Config.log.warning("Failed to remove old volume.")

    def create_rds_snapshot(self, additional_tags):
        now = datetime.now()
        current_time = now.strftime("%d-%m-%Y-%H-%M-%S")

        tags = []
        for tag_key, tag_value in additional_tags.items():
            if tag_value:
                tags.append({
                    'Key': tag_key,
                    'Value': tag_value
                })

        try:
            response = self.rds_client.create_db_snapshot(
                DBSnapshotIdentifier=f"Dataiku-database-{current_time}",
                DBInstanceIdentifier=Config.database_id,
                Tags=tags
            )
            return response['DBSnapshot']['DBSnapshotIdentifier']

        except botocore.exceptions.ClientError as err:
            Config.log.warning(f"Failed to create RDS snapshot: {err}")

    def remove_volume_tag(self, volume_id, tag_key, tag_value):
        try:
            response = self.ec2_client.delete_tags(
                Resources=[
                    volume_id
                ],
                Tags=[
                    {
                        'Key': tag_key,
                        'Value': tag_value
                    },
                ]
            )
            return response
        except botocore.exceptions.ClientError as err:
            Config.log.warning(f"Failed to remove tag from volume: {err}")
