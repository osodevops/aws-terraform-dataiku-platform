from aws import Aws
from config import Config
from event import Event
from exceptions import BackupException


class InstanceException(BackupException):
    pass


class Instance:
    event: Event
    aws_handler: Aws
    tags: dict

    def __init__(self, event: Event, aws_handler: Aws):
        self.event = event
        self.aws_handler = aws_handler
        self.tags = {}

    def validate_state(self, expected_state):
        if self.event.get_event_data('state') != expected_state:
            Config.log.warning(
                f"Refused to process event {self.event.get_event_data('state')} for {self.event.get_event_data('instance_id')}")
            raise InstanceException("Snapshot creation run completed with no actions", "Received wrong event type")

    def validate_region(self, expected_region):
        if self.event.get_event_data('region') != expected_region:
            raise InstanceException("Snapshot creation run completed with no actions", "Instance is in wrong region")

    def validate_tags(self, tags_to_match: dict):
        self.tags = self.aws_handler.get_instance_tags(self.event.instance_id)

        for key, value in tags_to_match.items():
            Config.log.debug(f"Matching {key}, {value}")
            if type(value) == list:
                Config.log.debug(f"List {self.tags.get(key)}")
                if self.tags.get(key) not in value:
                    raise InstanceException("Snapshot creation run completed with no actions", "Incorrect tags")
            else:
                Config.log.debug(f"Single {self.tags.get(key)}")
                if self.tags.get(key) != value:
                    raise InstanceException("Snapshot creation run completed with no actions", "Incorrect tags")

        return True
