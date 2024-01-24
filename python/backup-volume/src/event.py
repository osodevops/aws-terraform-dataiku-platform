from config import Config
from aws import Aws


class Event:
    instance_id: str
    state: str
    az: [str, None]
    aws_handler: Aws

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
    #         "state": "terminated"
    #     }
    # }

    def __init__(self, event, aws_handler):
        Config.log.debug("Instantiating Event")
        self.instance_id = event['detail']['instance-id']
        self.state = event['detail']['state']
        self.az = None
        self.aws_handler = aws_handler
        self.region = event['region']

    def get_instance_id(self):
        return self.instance_id

    def get_event_data(self, key=False):
        if not self.az:
            self.az = self.aws_handler.get_az_from_instance(self.instance_id)

        dataset = {
            'state': self.state,
            'instance_id': self.instance_id,
            'az': self.az,
            'region': self.region
        }

        if key:
            return dataset[key]

        return dataset

    def check_tags(self):
        tags = self.aws_handler.get_instance_tags(self.instance_id)
        if tags.get('Environment', "") == Config.tag_environment and \
                tags.get('Deployment', "") == Config.tag_deployment and \
                tags.get('Application') == Config.tag_application:
            return True
        return False
