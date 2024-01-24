from unittest import mock

import botocore
import boto3
import botocore.config
import pytest
from moto import mock_ec2, mock_sts

from src.aws import Aws
from src.exceptions import BackupException


class MockConfig:
    region = 'eu-west-2'
    boto_config = botocore.config.Config(
        region_name='eu-west-2',
        signature_version='v4',
        retries={
            'max_attempts': 4,
            'mode': 'standard'
        }
    )
    # Tag is "Data-volume": "thing"
    tag_data_volume = 'foo_volume'
    tag_application = 'foo_application'
    tag_environment = 'foo_environment'


@mock_ec2
@mock_sts
def test_aws():
    aws_obj = Aws()
    assert True


@mock_ec2
@mock_sts
def test_get_az_from_instance_success():
    aws_obj = Aws()

    ec2 = boto3.resource('ec2')
    test_server = ec2.create_instances(
        ImageId='ami-xxxxx', MinCount=1, MaxCount=1,
        Placement={'AvailabilityZone': 'eu-west-2c'}
    )

    ec2.create_tags(
        Resources=[test_server[0].id],
        Tags=[{'Key': 'Name', 'Value': 'testserver1'}])

    assert aws_obj.get_az_from_instance(instance_id=test_server[0].id) == 'eu-west-2c'


@mock_ec2
@mock_sts
def test_get_az_from_instance_failure():
    aws_obj = Aws()

    with pytest.raises(botocore.exceptions.ClientError):
        aws_obj.get_az_from_instance(instance_id='nope')


@mock_ec2
@mock_sts
def test_get_snapshot_data_no_data():
    aws_obj = Aws()

    with pytest.raises(botocore.exceptions.ClientError):
        response = aws_obj.get_snapshot_data(snapshot_id="foo_id")
        response = aws_obj.get_snapshot_data(additional_tags={"fail": "now"})


@mock_ec2
@mock_sts
def test_get_snapshot_data_success():
    aws_obj = Aws()

    volume_id = aws_obj.ec2_client.create_volume(
        AvailabilityZone='eu-west-2',
        Encrypted=False,
        Size=123,
        VolumeType='gp3',
    )['VolumeId']

    snapshot_id = aws_obj.ec2_client.create_snapshot(
        Description='foo',
        VolumeId=volume_id,
        TagSpecifications=[
            {
                'ResourceType': 'snapshot',
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
            },
        ],
    )['SnapshotId']

    response = aws_obj.get_snapshot_data(additional_tags={'tag_a': 'foo_a', 'tag_b': 'foo_b', 'tag_c': 'foo_c'})
    assert response['Snapshots'][0]['Tags'] == [
        {'Key': 'tag_a', 'Value': 'foo_a'},
        {'Key': 'tag_b', 'Value': 'foo_b'},
        {'Key': 'tag_c', 'Value': 'foo_c'}]
    assert response['Snapshots'][0]['SnapshotId'] == snapshot_id

    response = aws_obj.get_snapshot_data(additional_tags={'tag_a': 'foo_a', 'tag_b': 'foo_b', 'tag_c': None})
    assert response['Snapshots'][0]['Tags'] == [
        {'Key': 'tag_a', 'Value': 'foo_a'},
        {'Key': 'tag_b', 'Value': 'foo_b'},
        {'Key': 'tag_c', 'Value': 'foo_c'}]
    assert response['Snapshots'][0]['SnapshotId'] == snapshot_id

    response = aws_obj.get_snapshot_data(snapshot_id=snapshot_id)
    assert response['Snapshots'][0]['Tags'] == [
        {'Key': 'tag_a', 'Value': 'foo_a'},
        {'Key': 'tag_b', 'Value': 'foo_b'},
        {'Key': 'tag_c', 'Value': 'foo_c'}]
    assert response['Snapshots'][0]['SnapshotId'] == snapshot_id



@mock_ec2
@mock_sts
def test_get_volume_data_no_data():
    aws_obj = Aws()

    with pytest.raises(botocore.exceptions.ClientError):
        response = aws_obj.get_volume_data(az='eu-west-2a', volume_id='foobar_vid', instance_id='foobar_iid')

    with pytest.raises(botocore.exceptions.ClientError):
        response = aws_obj.get_volume_data(az='eu-west-2a', volume_id='foobar_vid')

    response = aws_obj.get_volume_data(az='eu-west-2a', instance_id='foobar_iid')
    assert not response['Volumes']

    response = aws_obj.get_volume_data(az='eu-west-2a')
    assert not response['Volumes']


@mock_ec2
@mock_sts
def test_get_volume_data_success():
    aws_obj = Aws()

    volume_id = aws_obj.ec2_client.create_volume(
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
                        'Value': 'Dataiku'
                    },
                    {
                        'Key': 'Environment',
                        'Value': 'test'
                    },
                    {
                        'Key': 'Deployment',
                        'Value': ''
                    },
                    {
                        'Key': 'Data-volume',
                        'Value': 'design'
                    },
                    {
                        'Key': 'Instance',
                        'Value': '123456'
                    }
                ]
            },
        ],
    )['VolumeId']

    response = aws_obj.get_volume_data(az='eu-west-2a')
    assert response['Volumes'][0]['Tags'] == [
        {'Key': 'Application', 'Value': 'Dataiku'},
        {'Key': 'Environment', 'Value': 'test'},
        {'Key': 'Deployment', 'Value': ''},
        {'Key': 'Data-volume', 'Value': 'design'},
        {'Key': 'Instance', 'Value': '123456'}]
    assert response['Volumes'][0]['VolumeId'] == volume_id

    response = aws_obj.get_volume_data(az='eu-west-2a', volume_id=volume_id)
    assert response['Volumes'][0]['Tags'] == [
        {'Key': 'Application', 'Value': 'Dataiku'},
        {'Key': 'Environment', 'Value': 'test'},
        {'Key': 'Deployment', 'Value': ''},
        {'Key': 'Data-volume', 'Value': 'design'},
        {'Key': 'Instance', 'Value': '123456'}]
    assert response['Volumes'][0]['VolumeId'] == volume_id

    response = aws_obj.get_volume_data(az='eu-west-2a', instance_id='123456')
    assert response['Volumes'][0]['Tags'] == [
        {'Key': 'Application', 'Value': 'Dataiku'},
        {'Key': 'Environment', 'Value': 'test'},
        {'Key': 'Deployment', 'Value': ''},
        {'Key': 'Data-volume', 'Value': 'design'},
        {'Key': 'Instance', 'Value': '123456'}]
    assert response['Volumes'][0]['VolumeId'] == volume_id


@mock_ec2
@mock_sts
def test_get_instance_success():
    aws_obj = Aws()

    ec2 = boto3.resource('ec2')
    test_server = ec2.create_instances(
        ImageId='ami-xxxxx', MinCount=1, MaxCount=1,
        Placement={'AvailabilityZone': 'eu-west-2c'}
    )

    instance = aws_obj.get_instance(instance_id=test_server[0].id)

    assert instance['InstanceId'] == test_server[0].id


@mock_ec2
@mock_sts
def test_get_instance_failure():
    aws_obj = Aws()

    with pytest.raises(botocore.exceptions.ClientError):
        instance = aws_obj.get_instance(instance_id='foonope')


@mock_ec2
@mock_sts
@mock.patch('src.aws.Aws.get_instance', return_value={
    'Tags': [
        {'Key': '1', 'Value': '2'},
        {'Key': '3', 'Value': '4'}
    ]})
def test_get_instance_tags_success(mock_get_instance):
    aws_obj = Aws()

    tags = aws_obj.get_instance_tags(instance_id='foobar')

    assert tags == {'1': '2', '3': '4'}


@mock_ec2
@mock_sts
@mock.patch('src.aws.Aws.get_instance', return_value={'Tags': []})
def test_get_instance_tags_no_data(mock_get_instance):
    aws_obj = Aws()

    tags = aws_obj.get_instance_tags(instance_id='foobar')

    assert tags == {}


@mock_ec2
@mock_sts
def test_create_snapshot_success():
    aws_obj = Aws()

    volume_id = aws_obj.ec2_client.create_volume(
        AvailabilityZone='eu-west-2',
        Encrypted=False,
        Size=123,
        VolumeType='gp3',
    )['VolumeId']

    snapshot_id = aws_obj.create_snapshot(volume_id=volume_id)
    assert snapshot_id

    snapshot_id = aws_obj.create_snapshot(volume_id=volume_id, additional_tags={'tag_a': 'foo'})
    assert snapshot_id
    response = aws_obj.get_snapshot_data(snapshot_id=snapshot_id)
    assert response['Snapshots'][0]['Tags'] == [{'Key': 'tag_a', 'Value': 'foo'}]


@mock_ec2
@mock_sts
def test_create_snapshot_failure():
    aws_obj = Aws()

    volume_id = aws_obj.ec2_client.create_volume(
        AvailabilityZone='eu-west-2',
        Encrypted=False,
        Size=123,
        VolumeType='gp3',
    )['VolumeId']

    with pytest.raises(botocore.exceptions.ClientError):
        _ = aws_obj.create_snapshot(volume_id='foonope')
