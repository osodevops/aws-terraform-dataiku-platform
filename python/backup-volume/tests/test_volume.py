import time

import pytest
from moto import mock_ec2, mock_sts

from exceptions import BackupException
from src.aws import Aws
from src.volume import Volume


@mock_ec2
@mock_sts
def test_most_recent_volume_is_returned():
    aws_handler = Aws()
    instance_id = "i-abc123"

    for i in range(2):
        vol_id = aws_handler.ec2_client.create_volume(
            AvailabilityZone='eu-west-2a',
            Encrypted=False,
            Size=123,
            VolumeType='gp3',
            TagSpecifications=[
                {
                    'ResourceType': 'volume',
                    'Tags': [
                        {
                            'Key': 'Application',
                            'Value': 'Dataiku-DSS'
                        },
                        {
                            'Key': 'DssNode',
                            'Value': 'design'
                        },
                        {
                            'Key': 'Instance',
                            'Value': instance_id
                        },
                        {
                            'Key': 'Environment',
                            'Value': 'development'
                        },
                        {
                            'Key': 'Deployment',
                            'Value': 'dev'
                        },
                        {
                            'Key': 'Snapshot',
                            'Value': "true"
                        },
                        {
                            'Key': 'Volume',
                            'Value': 'old'
                        }
                    ]
                }
            ]
        )['VolumeId']
        time.sleep(1)

    volume_obj = Volume(
        event_data={
            'az': 'eu-west-2a',
            'instance_id': instance_id
        },
        aws_handler=aws_handler,
        search_tags={
            "Application": "Dataiku-DSS",
            "DssNode": "design",
            "Instance": instance_id,
            "Environment": "development",
            "Deployment": "dev",
            "Snapshot": "true"
        }
    )

    assert volume_obj.volume_id == vol_id


@mock_ec2
def test_if_no_volumes_are_found():
    aws_handler = Aws()

    az = "eu-west-2a"

    with pytest.raises(BackupException):
        volume_obj = Volume(
            {
                'az': az,
                'instance_id': 'fail'
            },
            aws_handler,
            {
                "Application": "Dataiku-DSS",
                "DssNode": "design",
                "Instance": 'fail',
                "Environment": "development",
                "Deployment": "dev",
                "Snapshot": "true"
            }
        )

