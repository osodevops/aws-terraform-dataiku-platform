import logging
import os
import sys

from instance import Instance
from aws import Aws
from snapshot import Snapshot
from local_volume import LocalVolume
from volume import Volume
from config import Config
from exceptions import HandlerException

logging.basicConfig(level=os.getenv("LOG_LEVEL", logging.INFO))
logger = logging.getLogger(__name__)


def load_config():
    """Load and return the application configuration."""
    return Config()


def initialize_aws_resources(config):
    """Initialize and return AWS-related resources."""
    aws_handler = Aws(config)
    instance = Instance(aws_handler)
    return aws_handler, instance


def manage_volume(instance, aws_handler, volume_tag_set, volume_mgr):
    """Manage the volume attachment and creation."""
    # Is there a volume attachment that matches the volume spec
    if aws_handler.match_volume_attachment(instance_id=instance.get_instance_id(), tag_set=volume_tag_set):
        logger.info(f"Volume is already attached. Exiting.")
        sys.exit(0)

    snapshot = Snapshot(aws_handler=aws_handler, tags=volume_tag_set)
    snapshot_id = ""

    if snapshot.exists():
        logger.info(f"Snapshot ID: {snapshot.get_snapshot_data('snapshot_id')}")
        snapshot.wait_for_pending()
        if volume_mgr.get_volume(search_tag_set=volume_tag_set, snapshot_id=snapshot.get_snapshot_data('snapshot_id')):
            volume_mgr.delete()
        snapshot_id = snapshot.get_snapshot_data('snapshot_id')

    volume_mgr.create_volume(create_tag_set=volume_tag_set, snapshot_id=snapshot_id)
    logger.info(f"Volume {volume_mgr.get_volume_data('volume_id')} attached to instance {instance.get_instance_data('instance_id')} with snapshot {snapshot.get_snapshot_data('snapshot_id')}")
    volume_mgr.attach(instance.get_instance_data())


def manage_local_volume(volume_mgr, config):
    """Initialize and mount the local volume."""
    local_volume = LocalVolume(volume_data=volume_mgr.get_volume_data(), config=config)
    local_volume.initialise_filesystem()
    local_volume.mount(configure_fstab=True)
    local_volume.set_mount_ownership(user='dataiku', group='dataiku')


def main():
    try:
        config = load_config()
        aws_handler, instance = initialize_aws_resources(config)

        instance_tag_set = {
            'Environment': instance.tags['Environment'],
            'Name': instance.tags['Name'],
            'Application': 'Dataiku'
        }

        volume_tag_set = {
            'Environment': instance.tags['Environment'],
            'Name': instance.tags['Name'],
            'Application': 'Dataiku',
            'DataVolume': 'True'
        }

        # Prevent race condition when previous machine is slow terminating
        instance.wait_for_instances(states=['shutting-down', 'running'], additional_tags=instance_tag_set)
        volume_mgr = Volume(
            event_data=instance.get_instance_data(),
            aws_handler=aws_handler
        )
        manage_volume(instance, aws_handler, volume_tag_set, volume_mgr)
        manage_local_volume(volume_mgr, config)

    except HandlerException as e:
        logger.error(f"HandlerException: {e.message}", exc_info=True)


if __name__ == "__main__":
    main()
