import logging

import boto3
import botocore.config
from moto import mock_ec2, mock_sts

from src.aws import Aws
from src.config import Config


class MockConfig(Config):
    def __init__(self, region):
        self.region = region

        # Tag settings


        # Volume settings
        self.encrypt_volumes = True
        self.volume_iops = 500
        self.kms_key = 'default'
        self.volume_type = 'gp3'
        self.volume_size = '50'
        self.volume_device_name = 'foo-device-name'
        self.volume_mount_point = '/dev/sda/'

        self.boto_config = botocore.config.Config(
            region_name=self.region,
            signature_version='v4',
            retries={
                'max_attempts': 4,
                'mode': 'standard'
            }
        )

        logging.basicConfig(level='INFO')
        self.log = logging.getLogger(__name__)
        self.log.setLevel(logging.INFO)
        logging.getLogger("botocore").setLevel(logging.WARNING)

@mock_ec2
@mock_sts
def test_get_instance_id_with_exclude():
    config = MockConfig(
        region='eu-west-2'
    )
    aws_client = Aws(config)

    vpc_response =  aws_client.ec2_client.create_vpc(
        CidrBlock='192.168.0.0/16',
    )

    subnet_response = aws_client.ec2_client.create_subnet(
        CidrBlock='192.168.1.0/24',
        VpcId=vpc_response['Vpc']['VpcId']
    )

    ec2_response = aws_client.ec2_client.run_instances(
        ImageId='ami-03cf127a',
        InstanceType='t3.medium',
        SubnetId=subnet_response['Subnet']['SubnetId'],
        MaxCount=1,
        MinCount=1,
    )

    instance_id = ec2_response['Instances'][0]['InstanceId']

    assert aws_client.get_instance_id(
        ['running'],
        additional_tags={},
        exclude_id=instance_id) is None

    assert aws_client.get_instance_id(
        ['running'],
        additional_tags={}) == instance_id


@mock_ec2
@mock_sts
def test_get_instance_id_with_deployments():
    config = MockConfig(
        region='eu-west-2'
    )
    aws_client = Aws(config)

    vpc_response =  aws_client.ec2_client.create_vpc(
        CidrBlock='192.168.0.0/16',
    )

    subnet_response = aws_client.ec2_client.create_subnet(
        CidrBlock='192.168.1.0/24',
        VpcId=vpc_response['Vpc']['VpcId']
    )

    # Add wrong instances
    for tag_a, tag_b, tag_c in [
        ['', '', ''],
        ['', 'foo_b', ''],
        ['', 'wrong', ''],
        ['foo_a', 'foo_b', ''],
        ['wrong', 'foo_b', ''],
        ['wrong', 'foo_b', 'foo_c'],
        ['wrong', 'wrong', 'wrong']
    ]:

        tags = [
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'tag_a',
                            'Value': tag_a
                        },
                        {
                            'Key': 'tag_b',
                            'Value': tag_b
                        },
                        {
                            'Key': 'tag_c',
                            'Value': tag_c
                        }
                    ]
                }
            ]

        aws_client.ec2_client.run_instances(
            ImageId='ami-03cf127a',
            InstanceType='t3.medium',
            SubnetId=subnet_response['Subnet']['SubnetId'],
            MaxCount=1,
            MinCount=1,
            TagSpecifications=tags
        )

    assert aws_client.get_instance_id(['running'], additional_tags={'tag_a': 'foo_a', 'tag_b': 'foo_b', 'tag_c': 'foo_c'}) is None

    # Define correct instance
    ec2_response = aws_client.ec2_client.run_instances(
            ImageId='ami-03cf127a',
            InstanceType='t3.medium',
            SubnetId=subnet_response['Subnet']['SubnetId'],
            MaxCount=1,
            MinCount=1,
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'tag_a',
                            'Value': "foo_a"
                        },
                        {
                            'Key': 'tag_b',
                            'Value': "foo_b"
                        },
                        {
                            'Key': 'tag_c',
                            'Value': "foo_c"
                        }
                    ]
                }
            ]
        )

    assert aws_client.get_instance_id(['running'], additional_tags={'tag_a': 'foo_a', 'tag_b': 'foo_b', 'tag_c': 'foo_c'}) == ec2_response['Instances'][0]['InstanceId']
    assert not aws_client.get_instance_id(['notrunning'], additional_tags={'tag_a': 'foo_a', 'tag_b': 'foo_b', 'tag_c': 'foo_c'})


@mock_ec2
@mock_sts
def test_get_instance_id_null_tag():
    config = MockConfig(
        region='eu-west-2'
    )
    aws_client = Aws(config)

    vpc_response =  aws_client.ec2_client.create_vpc(
        CidrBlock='192.168.0.0/16',
    )

    subnet_response = aws_client.ec2_client.create_subnet(
        CidrBlock='192.168.1.0/24',
        VpcId=vpc_response['Vpc']['VpcId']
    )

    # Define correct instance
    ec2_response = aws_client.ec2_client.run_instances(
            ImageId='ami-03cf127a',
            InstanceType='t3.medium',
            SubnetId=subnet_response['Subnet']['SubnetId'],
            MaxCount=1,
            MinCount=1,
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'tag_a',
                            'Value': 'foo_a'
                        },
                        {
                            'Key': 'tag_b',
                            'Value': 'foo_b'
                        },
                        {
                            'Key': 'tag_c',
                            'Value': 'foo_c'
                        },
                    ]
                }
            ]
        )

    assert aws_client.get_instance_id(
        ['running'],
        additional_tags={'tag_a': 'foo_a', 'tag_b': 'foo_b', 'tag_c': None}
    ) == ec2_response['Instances'][0]['InstanceId']
    assert aws_client.get_instance_id(['notrunning'], additional_tags={'tag_a': 'foo_a', 'tag_b': 'foo_b', 'tag_c': None}) is None


@mock_ec2
@mock_sts
def test_get_volume_data_deployments():
    config = MockConfig(
        region='eu-west-2'
    )
    aws_client = Aws(config)

    # Create wrong entries
    for tag_a, tag_b, tag_c in [
        ['', '', ''],
        ['', 'foo_b', ''],
        ['', 'wrong', ''],
        ['foo_a', 'foo_b', ''],
        ['wrong', 'foo_b', ''],
        ['wrong', 'foo_b', 'foo_c'],
        ['wrong', 'wrong', 'wrong']
    ]:
        tags = [
                    {
                        'Key': 'tag_a',
                        'Value': tag_a
                    },
                    {
                        'Key': 'tag_b',
                        'Value': tag_b
                    },
                    {
                        'Key': 'tag_c',
                        'Value': tag_c
                    }
                ]

        aws_client.ec2_client.create_volume(
            AvailabilityZone='eu-west-2a',
            Size=50,
            VolumeType='gp3',
            TagSpecifications=[
                {
                    'ResourceType': 'volume',
                    'Tags': tags
                }
            ])

    assert aws_client.get_volume_data(
        az='eu-west-2a',
        search_tags={'tag_a': 'foo_a', 'tag_b': 'foo_b', 'tag_c': 'foo_c'}
    ) is None

    # Create correct entry
    response = aws_client.ec2_client.create_volume(
        AvailabilityZone='eu-west-2a',
        Size=50,
        VolumeType='gp3',
        TagSpecifications=[
            {
                'ResourceType': 'volume',
                'Tags': [
                    {
                        'Key': 'tag_a',
                        'Value': 'foo_a'
                    },
                    {
                        'Key': 'tag_b',
                        'Value': 'foo_b'
                    },
                    {
                        'Key': 'tag_c',
                        'Value': 'foo_c'
                    }
                ]
            }
        ]
    )

    assert aws_client.get_volume_data('eu-west-2a', volume_id=response['VolumeId'])['Volumes'][0]['VolumeId'] == response['VolumeId']
    assert aws_client.get_volume_data('eu-west-2a',
                                      search_tags={'tag_a': 'foo_a', 'tag_b': 'foo_b', 'tag_c': 'foo_c'}
                                      )['Volumes'][0]['VolumeId'] == response['VolumeId']

    assert len(aws_client.get_volume_data('eu-west-2a')['Volumes']) == 8
    assert aws_client.get_volume_data('eu-west-2a', volume_id='fail') is None
    assert aws_client.get_volume_data('eu-west-2b', search_tags={'tag_a': 'foo_a', 'tag_b': 'foo_b', 'tag_c': 'foo_c'}) is None


@mock_ec2
@mock_sts
def test_get_volume_data_environments():
    config = MockConfig(
        region='eu-west-2'
    )
    aws_client = Aws(config)

    # Create correct entry
    response = aws_client.ec2_client.create_volume(
        AvailabilityZone='eu-west-2a',
        Size=50,
        VolumeType='gp3',
        TagSpecifications=[
            {
                'ResourceType': 'volume',
                'Tags': [
                    {
                        'Key': 'tag_a',
                        'Value': 'foo_a'
                    },
                    {
                        'Key': 'tag_b',
                        'Value': 'foo_b'
                    },
                    {
                        'Key': 'tag_c',
                        'Value': 'foo_c'
                    }
                ]
            }
        ]
    )

    assert aws_client.get_volume_data('eu-west-2a',
                                      search_tags={'tag_a': 'foo_a', 'tag_b': 'foo_b', 'tag_c': None}
                                      )['Volumes'][0]['VolumeId'] == response['VolumeId']


@mock_ec2
@mock_sts
def test_get_snapshot_data_deployments():
    config = MockConfig(
        region='eu-west-2'
    )
    aws_client = Aws(config)

    vol_response = aws_client.ec2_client.create_volume(
        AvailabilityZone='eu-west-2a',
        Size=50,
        VolumeType='gp3'
    )

    # Assert on no snapshots
    assert aws_client.get_snapshot_data(search_tags={'tag_a': 'foo_a', 'tag_b': 'foo_b', 'tag_c': 'foo_c'}) is None

    # Create wrong entries
    for tag_a, tag_b, tag_c in [
        ['', '', ''],
        ['', 'foo_b', ''],
        ['', 'wrong', ''],
        ['foo_a', 'foo_b', ''],
        ['wrong', 'foo_b', ''],
        ['wrong', 'foo_b', 'foo_c'],
        ['wrong', 'wrong', 'wrong']
    ]:
        tags = [
                    {
                        'Key': 'tag_a',
                        'Value': tag_a
                    },
                    {
                        'Key': 'tag_b',
                        'Value': tag_b
                    },
                    {
                        'Key': 'tag_c',
                        'Value': tag_c
                    }
                ]

        aws_client.ec2_client.create_snapshot(
            VolumeId=vol_response['VolumeId'],
            TagSpecifications=[
                {
                    'ResourceType': 'snapshot',
                    'Tags': tags
                }
            ]
        )

    assert aws_client.get_snapshot_data(search_tags={'tag_a': 'foo_a', 'tag_b': 'foo_b', 'tag_c': 'foo_c'}) is None

    # Create correct entry
    response = aws_client.ec2_client.create_snapshot(
            VolumeId=vol_response['VolumeId'],
            TagSpecifications=[{
                'ResourceType': 'snapshot',
                'Tags': [{
                        'Key': 'tag_a',
                        'Value': 'foo_a'
                    },
                    {
                        'Key': 'tag_b',
                        'Value': 'foo_b'
                    },
                    {
                        'Key': 'tag_c',
                        'Value': 'foo_c'
                    }]
            }]
        )


    assert aws_client.get_snapshot_data(snapshot_id=response['SnapshotId'])['Snapshots'][0]['SnapshotId'] == response['SnapshotId']
    assert aws_client.get_snapshot_data(search_tags={'tag_a': 'foo_a', 'tag_b': 'foo_b', 'tag_c': 'foo_c'})['Snapshots'][0]['SnapshotId'] == response['SnapshotId']
    assert aws_client.get_snapshot_data(snapshot_id='fail', search_tags={'tag_a': 'foo_a', 'tag_b': 'foo_b', 'tag_c': 'foo_c'}) is None


@mock_ec2
@mock_sts
def test_get_snapshot_data_environments():
    config = MockConfig(
        region='eu-west-2'
    )
    aws_client = Aws(config)

    vol_response = aws_client.ec2_client.create_volume(
        AvailabilityZone='eu-west-2a',
        Size=50,
        VolumeType='gp3'
    )

    # Create correct entry
    response = aws_client.ec2_client.create_snapshot(
            VolumeId=vol_response['VolumeId'],
            TagSpecifications=[{
                'ResourceType': 'snapshot',
                'Tags': [{
                        'Key': 'tag_a',
                        'Value': 'foo_a'
                    },
                    {
                        'Key': 'tag_b',
                        'Value': 'foo_b'
                    },
                    {
                        'Key': 'tag_c',
                        'Value': 'foo_c'
                    }]
    }]
        )

    assert aws_client.get_snapshot_data(
        search_tags={'tag_a': 'foo_a', 'tag_b': 'foo_b', 'tag_c': None}
    )['Snapshots'][0]['SnapshotId'] == response['SnapshotId']


@mock_ec2
@mock_sts
def test_create_volume_from_snapshot_deployments():
    config = MockConfig(
        region='eu-west-2'
    )
    aws_client = Aws(config)

    vpc_response =  aws_client.ec2_client.create_vpc(
        CidrBlock='192.168.0.0/16',
    )

    subnet_response = aws_client.ec2_client.create_subnet(
        CidrBlock='192.168.1.0/24',
        VpcId=vpc_response['Vpc']['VpcId']
    )

    ec2_response = aws_client.ec2_client.run_instances(
        ImageId='ami-03cf127a',
        InstanceType='t3.medium',
        SubnetId=subnet_response['Subnet']['SubnetId'],
        MaxCount=1,
        MinCount=1,
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'tag_a',
                        'Value': 'foo_a'
                    },
                    {
                        'Key': 'tag_b',
                        'Value': 'foo_b'
                    },
                    {
                        'Key': 'tag_c',
                        'Value': 'foo_c'
                    }
                ]
            }
        ]
    )

    vol_response = aws_client.ec2_client.create_volume(
        AvailabilityZone='eu-west-2a',
        Size=50,
        VolumeType='gp3'
    )

    snapshot_response = aws_client.ec2_client.create_snapshot(
        VolumeId=vol_response['VolumeId'])

    volume_id = aws_client.create_volume_from_snapshot(
        az='eu-west-2a',
        snapshot_id=snapshot_response['SnapshotId'],
        instance_id=ec2_response['Instances'][0]['InstanceId'],
        tags={
            'tag_a': 'foo_a',
            'tag_b': 'foo_b',
            'tag_c': 'foo_c'
        }
    )
    new_vol_response = aws_client.get_volume_data('eu-west-2a', volume_id=volume_id)
    assert new_vol_response['Volumes'][0]['VolumeId'] == volume_id
    assert {'Key': 'Snapshot', 'Value': 'true'} in new_vol_response['Volumes'][0]['Tags']
    assert {'Key': 'tag_a', 'Value': 'foo_a'} in new_vol_response['Volumes'][0]['Tags']
    assert {'Key': 'tag_b', 'Value': 'foo_b'} in new_vol_response['Volumes'][0]['Tags']
    assert {'Key': 'tag_c', 'Value': 'foo_c'} in new_vol_response['Volumes'][0]['Tags']


@mock_ec2
@mock_sts
def test_get_volume_data_no_volumes():
    config = MockConfig(
        region='eu-west-2'
    )
    aws_client = Aws(config)

    assert aws_client.get_volume_data('eu-west-2a') is None
