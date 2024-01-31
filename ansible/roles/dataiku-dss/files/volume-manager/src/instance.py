import logging
import time

import requests
from aws import Aws

logger = logging.getLogger(__name__)


class Instance:
    instance_id: [str, None]
    action: str
    az: [str, None]
    aws_handler: Aws
    sleep_wait_period: int = 30
    tags: dict

    # Incoming event
    # {
    #     "id": "7bf73129-1428-4cd3-a780-95db273d1602",
    #     "detail-type": "EC2 Instance State-change Notification",
    #     "source": "aws.ec2",
    #     "account": "123456789012",
    #     "time": "2019-11-11T21:29:54Z",
    #     "region": "us-east-1",
    #     "resources": [
    #         "arn:aws:ec2:us-east-1:123456789012:instance/i-abcd1111"
    #     ],
    #     "detail": {
    #         "instance-id": "i-abcd1111",
    #         "state": "pending"
    #     }
    # }

    def __init__(self, aws_handler):
        self.az = None
        self.aws_handler = aws_handler
        self.instance_id = None
        response = requests.get('http://169.254.169.254/latest/meta-data/instance-id')
        self.instance_id = response.text
        self.tags = self.format_tags(self.aws_handler.get_instance_tags(self.instance_id))

    @staticmethod
    def format_tags(tags):
        dataset = {}
        for tag in tags:
            dataset[tag['Key']] = tag['Value']
        return dataset

    def wait_for_instances(self, states=[], additional_tags={}, max_attempts=30):
        attempts = 1
        while self.aws_handler.get_instance_id(states=states, additional_tags=additional_tags, exclude_id=self.instance_id):
            logger.warning("Waiting for instances in state %s" % states)
            time.sleep(self.sleep_wait_period)
            if attempts >= max_attempts:
                logger.warning('Reached maximum number of retries waiting for instance')
                break
            attempts += 1

    def get_instance_id(self):
        return self.instance_id

    def get_instance_data(self, key=False):
        if not self.az:
            self.az = self.aws_handler.get_az_from_instance(self.instance_id)

        dataset = {
            'instance_id': self.instance_id,
            'az': self.az
        }

        if key:
            return dataset[key]

        return dataset
