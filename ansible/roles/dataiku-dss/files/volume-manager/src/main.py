import logging
import sys

from instance import Instance
from aws import Aws
from snapshot import Snapshot
from local_volume import LocalVolume
from volume import Volume
from config import Config


class HandlerException(Exception):
    def __init__(self, message, errors):
        super().__init__(message)
        self.errors = errors
        print('Handler Errors:')
        print(errors)


def main():
    logging.info("Starting run")

    config = Config()
    aws_handler = Aws(config)
    instance = Instance(aws_handler)

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
    instance.wait_for_instances(
        states=['shutting-down', 'running'],
        additional_tags=instance_tag_set)

    # Is there a volume attachment that matches the volume spec
    if aws_handler.match_volume_attachment(instance_id=instance.get_instance_id(), tag_set=volume_tag_set):
        logging.info(f"Volume is already attached. Exiting.")
        sys.exit(0)

    snapshot = Snapshot(
        aws_handler=aws_handler,
        tags=volume_tag_set)

    volume_mgr = Volume(
        event_data=instance.get_instance_data(),
        aws_handler=aws_handler
    )

    # Snapshot is the source of truth. If it doesnt exist, create a new volume
    if snapshot.exists():
        # Wait for snapshot, if its still creating
        logging.info(f"Got snapshot id: {snapshot.get_snapshot_data('snapshot_id')}")
        logging.info("Waiting for snapshot to complete")
        snapshot.wait_for_pending()

        # Remove prior volume that used the snapshot
        if volume_mgr.get_volume(
                search_tag_set=volume_tag_set,
                snapshot_id=snapshot.get_snapshot_data('snapshot_id')):
            logging.info("Removing legacy volume tied to snapshot")
            volume_mgr.delete()

    # Create a new volume
    volume_mgr.create_volume(create_tag_set=volume_tag_set)

    logging.info(f"Volume {volume_mgr.get_volume_data('volume_id')},"
                 f" instance {instance.get_instance_data('instance_id')},"
                 f" snapshot {snapshot.get_snapshot_data('snapshot_id')}")

    logging.info("Attaching volume")
    volume_mgr.attach(instance.get_instance_data())

    local_volume = LocalVolume(volume_data=volume_mgr.get_volume_data(), config=config)

    logging.info("Creating / resizing filesystem")
    local_volume.initialise_filesystem()

    logging.info("Mounting filesystem")
    local_volume.mount(configure_fstab=True)
    local_volume.set_mount_ownership(user='dataiku', group='dataiku')


if __name__ == "__main__":
    main()
