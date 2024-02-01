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

        instance_validation_tags = {
            'Application': 'Dataiku',
            Config.tag_target: ['True']
        }

        # instance tags must match Application, and custom tag - TODO
        instance.validate_tags(instance_validation_tags)

        Config.log.info(f"Found instance termination event for {event.get_event_data('instance_id')}")

        Config.log.info(f"Getting volume")

        # volume must match everything
        volume_search_tags = {
            'Environment': instance.tags['Environment'],
            'Name': instance.tags['Name'],
            'Application': 'Dataiku',
            'DataVolume': 'True',
        }
        volume = Volume(event.get_event_data(), aws_handler, search_tags=volume_search_tags)

        Config.log.info(f"Creating snapshot")
        # New snapshot must have all tags required by volume manager
        snapshot_id = volume.create_snapshot(additional_tags=volume_search_tags)
        volume.remove_snapshot_tag()
        Config.log.info(f"Created snapshot id: {snapshot_id}")

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