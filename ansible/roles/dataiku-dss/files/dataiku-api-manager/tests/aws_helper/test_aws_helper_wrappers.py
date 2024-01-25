import boto3
import botocore.client
import botocore.config

from moto import mock_ec2, mock_ssm, mock_elbv2, mock_s3

import aws_helper
from aws_helper.helper import ssm_client_wrapper, ec2_client_wrapper, lb_client_wrapper, s3_client_wrapper


@mock_ec2
@mock_ssm
@mock_elbv2
@mock_s3
def test_dss_client_decorator():
    class WrapperTester:
        ssm_client: [boto3.client, None] = None
        lb_client: [boto3.client, None] = None
        ec2_client: [boto3.client, None] = None
        s3_client: [boto3.client, None] = None
        boto_config = botocore.config.Config(
                region_name='eu-west-1',
                signature_version='v4',
                retries={
                    'max_attempts': 4,
                    'mode': 'standard'
                }
            )

        @ec2_client_wrapper
        def call_me_ec2(self):
            return

        @ssm_client_wrapper
        def call_me_ssm(self):
            return

        @lb_client_wrapper
        def call_me_lb(self):
            return

        @s3_client_wrapper
        def call_me_s3(self):
            return

    helper = WrapperTester()

    helper.call_me_ec2()
    assert isinstance(helper.ec2_client, botocore.client.BaseClient)

    helper.call_me_ssm()
    assert isinstance(helper.ssm_client, botocore.client.BaseClient)

    helper.call_me_lb()
    assert isinstance(helper.lb_client, botocore.client.BaseClient)

    helper.call_me_s3()
    assert isinstance(helper.lb_client, botocore.client.BaseClient)
