import pytest
from moto import mock_ec2, mock_elbv2

from aws_helper.exceptions import AwsHelperException
from aws_helper.helper import AwsHelper as Aws


@mock_ec2
def test_get_instance_id_with_exclude():
    aws_helper = Aws()
    aws_helper.get_clients()

    vpc_response = aws_helper.ec2_client.create_vpc(
        CidrBlock='192.168.0.0/16',
    )

    subnet_response = aws_helper.ec2_client.create_subnet(
        CidrBlock='192.168.1.0/24',
        VpcId=vpc_response['Vpc']['VpcId']
    )

    ec2_response = aws_helper.ec2_client.run_instances(
        ImageId='ami-03cf127a',
        InstanceType='t3.medium',
        SubnetId=subnet_response['Subnet']['SubnetId'],
        MaxCount=1,
        MinCount=1,
    )

    instance_id = ec2_response['Instances'][0]['InstanceId']

    assert aws_helper.get_instance_id(
        {
            'states': ['running'],
            'exclude_id': instance_id
        }
    ) is None

    assert aws_helper.get_instance_id(
        {
            'states': ['running']
        }
    ) == instance_id


@mock_ec2
def test_get_instance_id_with_deployments():
    aws_helper = Aws()
    aws_helper.get_clients()

    vpc_response = aws_helper.ec2_client.create_vpc(
        CidrBlock='192.168.0.0/16',
    )

    subnet_response = aws_helper.ec2_client.create_subnet(
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

        aws_helper.ec2_client.run_instances(
            ImageId='ami-03cf127a',
            InstanceType='t3.medium',
            SubnetId=subnet_response['Subnet']['SubnetId'],
            MaxCount=1,
            MinCount=1,
            TagSpecifications=tags
        )

    assert aws_helper.get_instance_id(
        {
            'states': ['running'],
            'additional_tags': {'tag_a': 'foo_a', 'tag_b': 'foo_b', 'tag_c': 'foo_c'}
        }
    ) is None

    # Define correct instance
    ec2_response = aws_helper.ec2_client.run_instances(
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

    assert aws_helper.get_instance_id(
        {
            'states': ['running'],
            'additional_tags': {'tag_a': 'foo_a', 'tag_b': 'foo_b', 'tag_c': 'foo_c'}
        }
    ) == ec2_response['Instances'][0]['InstanceId']

    assert not aws_helper.get_instance_id(
        {
            'states': ['notrunning'],
            'additional_tags': {'tag_a': 'foo_a', 'tag_b': 'foo_b', 'tag_c': 'foo_c'}
        }
    )


@mock_ec2
def test_get_instance_id_no_config():
    aws_helper = Aws()

    with pytest.raises(Exception):
        aws_helper.get_instance_id()


@mock_ec2
def test_get_instance_id_null_tag():
    aws_helper = Aws()
    aws_helper.get_clients()

    vpc_response = aws_helper.ec2_client.create_vpc(
        CidrBlock='192.168.0.0/16',
    )

    subnet_response = aws_helper.ec2_client.create_subnet(
        CidrBlock='192.168.1.0/24',
        VpcId=vpc_response['Vpc']['VpcId']
    )

    # Define correct instance
    ec2_response = aws_helper.ec2_client.run_instances(
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

    assert aws_helper.get_instance_id(
        {
            'states': ['running'],
            'additional_tags': {'tag_a': 'foo_a', 'tag_b': 'foo_b', 'tag_c': None}
        }
    ) == ec2_response['Instances'][0]['InstanceId']

    assert aws_helper.get_instance_id(
        {
            'states': ['notrunning'],
            'additional_tags': {'tag_a': 'foo_a', 'tag_b': 'foo_b', 'tag_c': None}
        }
    ) is None


@mock_ec2
def test_get_az_from_instance():
    aws_helper = Aws()
    aws_helper.get_clients()

    vpc_response = aws_helper.ec2_client.create_vpc(
        CidrBlock='192.168.0.0/16',
    )

    subnet_response = aws_helper.ec2_client.create_subnet(
        CidrBlock='192.168.1.0/24',
        VpcId=vpc_response['Vpc']['VpcId']
    )

    # Define correct instance
    response = aws_helper.ec2_client.run_instances(
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

    instance_id = response['Instances'][0]['InstanceId']
    az = response['Instances'][0]['Placement']['AvailabilityZone']

    assert aws_helper.get_az_from_instance(instance_id) == az


@mock_ec2
def test_get_instance_tags():
    aws_helper = Aws()
    aws_helper.get_clients()

    vpc_response = aws_helper.ec2_client.create_vpc(
        CidrBlock='192.168.0.0/16',
    )

    subnet_response = aws_helper.ec2_client.create_subnet(
        CidrBlock='192.168.1.0/24',
        VpcId=vpc_response['Vpc']['VpcId']
    )

    tags = [
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
    # Define correct instance
    response = aws_helper.ec2_client.run_instances(
            ImageId='ami-03cf127a',
            InstanceType='t3.medium',
            SubnetId=subnet_response['Subnet']['SubnetId'],
            MaxCount=1,
            MinCount=1,
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': tags
                }
            ]
        )

    instance_id = response['Instances'][0]['InstanceId']

    assert aws_helper.get_instance_tags(instance_id) == tags


@mock_ec2
@mock_elbv2
def test_get_load_balancers_success():
    aws_helper = Aws()
    aws_helper.get_clients()

    vpc_response = aws_helper.ec2_client.create_vpc(
        CidrBlock='192.168.0.0/16',
    )

    subnet1_response = aws_helper.ec2_client.create_subnet(
        CidrBlock='192.168.1.0/24',
        VpcId=vpc_response['Vpc']['VpcId']
    )
    subnet2_response = aws_helper.ec2_client.create_subnet(
        CidrBlock='192.168.2.0/24',
        VpcId=vpc_response['Vpc']['VpcId']
    )

    lb_response = aws_helper.lb_client.create_load_balancer(
        Name='my_lb',
        Subnets=[
            subnet1_response['Subnet']['SubnetId'],
            subnet2_response['Subnet']['SubnetId']
        ],
        Scheme='internal',

        Type='application',
        IpAddressType='ipv4',
    )

    assert aws_helper.get_load_balancers()['LoadBalancers'][0]['LoadBalancerName'] == 'my_lb'


@mock_ec2
@mock_elbv2
def test_get_load_balancers_failure():
    aws_helper = Aws()
    aws_helper.get_clients()

    assert aws_helper.get_load_balancers()['LoadBalancers'] == []


@mock_ec2
@mock_elbv2
def test_get_load_balancer_by_name_success():
    aws_helper = Aws()
    aws_helper.get_clients()

    vpc_response = aws_helper.ec2_client.create_vpc(
        CidrBlock='192.168.0.0/16',
    )

    subnet1_response = aws_helper.ec2_client.create_subnet(
        CidrBlock='192.168.1.0/24',
        VpcId=vpc_response['Vpc']['VpcId']
    )
    subnet2_response = aws_helper.ec2_client.create_subnet(
        CidrBlock='192.168.2.0/24',
        VpcId=vpc_response['Vpc']['VpcId']
    )

    lb_response = aws_helper.lb_client.create_load_balancer(
        Name='my_lb',
        Subnets=[
            subnet1_response['Subnet']['SubnetId'],
            subnet2_response['Subnet']['SubnetId']
        ],
        Scheme='internal',

        Type='application',
        IpAddressType='ipv4',
    )

    assert aws_helper.get_load_balancer_by_name('my_lb')[0]['LoadBalancerName'] == 'my_lb'


@mock_ec2
@mock_elbv2
def test_get_load_balancer_by_name_failure():
    aws_helper = Aws()
    aws_helper.get_clients()

    assert not aws_helper.get_load_balancer_by_name('my_lb')


@mock_ec2
def test_get_volume_data_deployments():
    aws_helper = Aws()
    aws_helper.get_clients()

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

        aws_helper.ec2_client.create_volume(
            AvailabilityZone='eu-west-2a',
            Size=50,
            VolumeType='gp3',
            TagSpecifications=[
                {
                    'ResourceType': 'volume',
                    'Tags': tags
                }
            ])

    assert aws_helper.get_volume_data(
        {
            'az': 'eu-west-2a',
            'search_tags': {'tag_a': 'foo_a', 'tag_b': 'foo_b', 'tag_c': 'foo_c'}
        }
    ) is None

    # Create correct entry
    response = aws_helper.ec2_client.create_volume(
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

    assert aws_helper.get_volume_data(
        {
            'az': 'eu-west-2a',
            'volume_id': response['VolumeId']
        }
    )['Volumes'][0]['VolumeId'] == response['VolumeId']

    assert aws_helper.get_volume_data(
        {
            'az': 'eu-west-2a',
            'search_tags': {'tag_a': 'foo_a', 'tag_b': 'foo_b', 'tag_c': 'foo_c'}
        }
    )['Volumes'][0]['VolumeId'] == response['VolumeId']

    assert len(aws_helper.get_volume_data({'az': 'eu-west-2a'})['Volumes']) == 8
    assert aws_helper.get_volume_data({'az': 'eu-west-2a', 'volume_id': 'fail'}) is None
    assert aws_helper.get_volume_data(
        {
            'az': 'eu-west-2b',
            'search_tags': {'tag_a': 'foo_a', 'tag_b': 'foo_b', 'tag_c': 'foo_c'}
        }
    ) is None


@mock_ec2
def test_get_volume_data_environments():
    aws_helper = Aws()
    aws_helper.get_clients()

    # Create correct entry
    response = aws_helper.ec2_client.create_volume(
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

    assert aws_helper.get_volume_data(
        {
            'az': 'eu-west-2a',
            'search_tags': {'tag_a': 'foo_a', 'tag_b': 'foo_b', 'tag_c': None}
        }
    )['Volumes'][0]['VolumeId'] == response['VolumeId']


@mock_ec2
def test_get_snapshot_data_deployments():
    aws_helper = Aws()
    aws_helper.get_clients()

    vol_response = aws_helper.ec2_client.create_volume(
        AvailabilityZone='eu-west-2a',
        Size=50,
        VolumeType='gp3'
    )

    # Assert on no snapshots
    assert aws_helper.get_snapshot_data(search_tags={'tag_a': 'foo_a', 'tag_b': 'foo_b', 'tag_c': 'foo_c'}) is None

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

        aws_helper.ec2_client.create_snapshot(
            VolumeId=vol_response['VolumeId'],
            TagSpecifications=[
                {
                    'ResourceType': 'snapshot',
                    'Tags': tags
                }
            ]
        )

    assert aws_helper.get_snapshot_data(search_tags={'tag_a': 'foo_a', 'tag_b': 'foo_b', 'tag_c': 'foo_c'}) is None

    # Create correct entry
    response = aws_helper.ec2_client.create_snapshot(
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

    assert aws_helper.get_snapshot_data(snapshot_id=response['SnapshotId'])['Snapshots'][0]['SnapshotId'] == response['SnapshotId']
    assert aws_helper.get_snapshot_data(search_tags={'tag_a': 'foo_a', 'tag_b': 'foo_b', 'tag_c': 'foo_c'})['Snapshots'][0]['SnapshotId'] == response['SnapshotId']
    assert aws_helper.get_snapshot_data(snapshot_id='fail', search_tags={'tag_a': 'foo_a', 'tag_b': 'foo_b', 'tag_c': 'foo_c'}) is None


@mock_ec2
def test_get_snapshot_data_environments():
    aws_helper = Aws()
    aws_helper.get_clients()

    vol_response = aws_helper.ec2_client.create_volume(
        AvailabilityZone='eu-west-2a',
        Size=50,
        VolumeType='gp3'
    )

    # Create correct entry
    response = aws_helper.ec2_client.create_snapshot(
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

    assert aws_helper.get_snapshot_data(
        search_tags={'tag_a': 'foo_a', 'tag_b': 'foo_b', 'tag_c': None}
    )['Snapshots'][0]['SnapshotId'] == response['SnapshotId']


@mock_ec2
def test_create_volume_from_snapshot_deployments():
    aws_helper = Aws()
    aws_helper.get_clients()

    vpc_response = aws_helper.ec2_client.create_vpc(
        CidrBlock='192.168.0.0/16',
    )

    subnet_response = aws_helper.ec2_client.create_subnet(
        CidrBlock='192.168.1.0/24',
        VpcId=vpc_response['Vpc']['VpcId']
    )

    ec2_response = aws_helper.ec2_client.run_instances(
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

    vol_response = aws_helper.ec2_client.create_volume(
        AvailabilityZone='eu-west-2a',
        Size=50,
        VolumeType='gp3'
    )

    snapshot_response = aws_helper.ec2_client.create_snapshot(
        VolumeId=vol_response['VolumeId'])

    volume_id = aws_helper.create_volume_from_snapshot(
        {
            'az': 'eu-west-2a',
            'snapshot_id': snapshot_response['SnapshotId'],
            'instance_id': ec2_response['Instances'][0]['InstanceId'],
            'tags': {
                'tag_a': 'foo_a',
                'tag_b': 'foo_b',
                'tag_c': 'foo_c'
            },
            'volume_type': 'gp3',
            'volume_size': '150',
            'encrypt_volumes': True,
            'kms_key': 'default',
            'volume_iops': '1050'
        })

    new_vol_response = aws_helper.get_volume_data({'az': 'eu-west-2a', 'volume_id': volume_id})
    assert new_vol_response['Volumes'][0]['VolumeId'] == volume_id
    assert {'Key': 'Snapshot', 'Value': 'true'} in new_vol_response['Volumes'][0]['Tags']
    assert {'Key': 'tag_a', 'Value': 'foo_a'} in new_vol_response['Volumes'][0]['Tags']
    assert {'Key': 'tag_b', 'Value': 'foo_b'} in new_vol_response['Volumes'][0]['Tags']
    assert {'Key': 'tag_c', 'Value': 'foo_c'} in new_vol_response['Volumes'][0]['Tags']


@mock_ec2
def test_get_volume_data_no_volumes():
    aws_helper = Aws()
    aws_helper.get_clients()

    assert aws_helper.get_volume_data({'az': 'eu-west-2a'}) is None
