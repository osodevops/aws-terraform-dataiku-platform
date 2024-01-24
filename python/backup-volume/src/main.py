import logging

from config import Config
from event import Event
from aws import Aws
from exceptions import BackupException
from rds import Rds
from instance import Instance
from volume import Volume

class HandlerException(Exception):
    def __init__(self, message, errors):
        super().__init__(message)
        self.errors = errors
        print('Handler Errors:')
        print(errors)


def lambda_handler(event, context):

    logging.info("Starting run")
    aws_handler = Aws()

    try:
        event = Event(event, aws_handler)
        instance = Instance(event, aws_handler)

        Config.log.info("Validating event")
        instance.validate_state('terminated')
        instance.validate_region(Config.region)
        instance.validate_tags({
            'Environment': Config.tag_environment,
            'Deployment': Config.tag_deployment,
            'Application': Config.tag_application,
            'DssNode': ['design', 'automation']
        })

        Config.log.info(f"Found instance termination event for {event.get_event_data('instance_id')}")

        Config.log.info(f"Getting volume")
        volume = Volume(event.get_event_data(), aws_handler, search_tags={
            'Application': Config.tag_application,
            'Environment': Config.tag_environment,
            'Deployment': Config.tag_deployment,
            'DssNode': instance.tags['DssNode']
        })

        Config.log.info(f"Creating snapshot")
        # todo
        snapshot_id = volume.create_snapshot(additional_tags={
            'Environment': Config.tag_environment,
            'Deployment': Config.tag_deployment,
            'Application': Config.tag_application,
            'DssNode': instance.tags['DssNode'],
            'Name': 'Dataiku-data-volume',
        })
        volume.remove_snapshot_tag()
        Config.log.info(f"Created snapshot id: {snapshot_id}")

        Config.log.info("Creating RDS snapshot")
        rds = Rds(aws_handler)
        rds_snapshot_id = rds.create_snapshot(additional_tags={
            'Environment': Config.tag_environment,
            'Deployment': Config.tag_deployment,
            'Application': Config.tag_application,
        })
        Config.log.info(f"Created RDS snapshot id: {rds_snapshot_id}")

        return {"Message": f"Snapshot creation run completed: Created snapshot id: {snapshot_id}"}
    except BackupException:
        return {"Message": f"No actions taken"}
    except Exception as err:
        Config.log.warning(f"An unexpected error occurred: {err}")
        aws_handler.raise_cloudwatch_alert()
        raise Exception(f"An unexpected error occurred: {err}")


if __name__ == "__main__":
    dummy_event = {
        "id": "7bf73129-1428-4cd3-a780-95db273d1602",
        "detail-type": "EC2 Instance State-change Notification",
        "source": "aws.ec2",
        "account": "123456789012",
        "time": "2019-11-11T21:29:54Z",
        "region": "eu-west-2",
        "resources": [
            "arn:aws:ec2:us-east-1:123456789012:instance/i-abcd1111"
        ],
        "detail": {
            "instance-id": "i-0bdbcc51fb975565b",
            "state": "terminated"
        }
    }
    dummy_context = {}
    # execute only if run as a script
    lambda_handler(dummy_event, dummy_context)