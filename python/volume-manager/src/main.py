import logging

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

    tag_set = {
        'Environment': instance.tags['Environment'],
        'Application': instance.tags['Application'],
        'Deployment': instance.tags['Deployment'],
        'DssNode': instance.tags['DssNode']
    }

    # Prevent race condition when previous machine is slow terminating
    instance.wait_for_instances(
        states=['shutting-down', 'running'],
        additional_tags=tag_set)

    snapshot = Snapshot(
        aws_handler=aws_handler,
        tags=tag_set)
    if snapshot.exists():
        logging.info(f"Got snapshot id: {snapshot.get_snapshot_data('snapshot_id')}")

    volume = Volume(
        event_data=instance.get_instance_data(),
        aws_handler=aws_handler,
        tags=tag_set)

    if snapshot.exists():
        logging.info("Waiting for snapshot to complete")
        snapshot.wait_for_pending()
        if volume.exists():
            # todo: Optimise for if the volume has valid data
            logging.info("Recreating volume with snapshot")
            volume.delete()
            volume.create_volume(
                snapshot_data=snapshot.get_snapshot_data(),
                instance_data=instance.get_instance_data()
            )
        else:
            # Snapshot exists, volume not exists
            #   create new volume from snapshot
            logging.info("Creating new volume from snapshot")
            volume.create_volume(
                snapshot_data=snapshot.get_snapshot_data(),
                instance_data=instance.get_instance_data()
            )
    else:
        if volume.exists():
            # Snapshot not exists, volume exists
            #   do nothing
            logging.info("No snapshot exists: Doing nothing")
        else:
            # Snapshot not exists, volume not exists
            #   create blank volume
            logging.info("Creating blank volume")
            volume.create_volume(
                instance_data=instance.get_instance_data()
            )

    logging.info(f"Volume {volume.get_volume_data('volume_id')},"
                 f" instance {instance.get_instance_data('instance_id')},"
                 f" snapshot {snapshot.get_snapshot_data('snapshot_id')}")

    logging.info("Attaching volume")
    volume.attach(instance.get_instance_data())

    local_volume = LocalVolume(volume_data=volume.get_volume_data(), config=config)

    logging.info("Creating / resizing filesystem")
    local_volume.initialise_filesystem()

    logging.info("Mounting filesystem")
    local_volume.mount(configure_fstab=True)
    local_volume.set_mount_ownership(user='dataiku', group='dataiku')


if __name__ == "__main__":
    main()
