import time

from aws import Aws
from exceptions import BackupException
from config import Config
from datetime import datetime
from dateutil.tz import tzutc


class Volume:
    volume_id: str
    aws_handler: Aws
    sleep_wait_period: int = 10

    def __init__(self, event_data: dict, aws_handler: Aws, search_tags: dict):
        self.vol_exists = False
        self.volume_id = ""
        self.creation_date = None
        self.aws_handler = aws_handler

        # Get all unattached volumes
        volume_data = aws_handler.get_volume_data(
            az=event_data['az'],
            instance_id=event_data['instance_id'],
            additional_tags=search_tags)['Volumes']

        if not volume_data:
            raise BackupException('Error', 'Could not find a data volume from this instance')

        volume = self._get_latest_volume(volume_data)
        if volume:
            volumeId = volume['VolumeId']
            Config.log.info(f"Lastest volume found {volumeId}")
            self.volume_id = volumeId
            return 

    @staticmethod
    def _get_latest_volume(data):
        Config.log.info('data from latest_volume: %s', data)
        # If only one volume is found, there is no need to compare the volumes to get the most recent.
        if len(data) == 1:
            return data[0]

        orderByDateTimeAndVolumeId = {}

        for d in data:
            if d['CreateTime'] and d['VolumeId']:
                # Set the format in an order that we can arrange - i.e %Y-%m-%d %H:%M:%S:volumeId.
                orderByDateTimeAndVolumeId.update({d['CreateTime'].strftime('%Y-%m-%d %H:%M:%S'):d['VolumeId']})

        # Then order the object by most recent date first. Get all of the keys (date and time) and sort them in reverse order, i.e most recent first.
        ordered_data = sorted(orderByDateTimeAndVolumeId.items(), key = lambda x:datetime.strptime(x[0], '%Y-%m-%d %H:%M:%S'), reverse=True)

        # Example of ordered data.
        # [('2022-09-08 15:55:15', 'vol-960b8600'), ('2022-09-08 15:55:13', 'vol-f9277c36'), ('2022-09-08 15:55:11', 'vol-1c89855c')]

        # Return the volumeID from the most recent volume.
        return {'VolumeId': ordered_data[0][1]}

    def create_snapshot(self, additional_tags={}, wait_for_completion=False):
        snapshot_id = self.aws_handler.create_snapshot(self.volume_id, additional_tags)

        if wait_for_completion:
            while self._get_snapshot_state(snapshot_id) != 'completed':
                Config.log.info('Waiting for Snapshot to create')
                time.sleep(self.sleep_wait_period)
        return snapshot_id

    def _get_snapshot_state(self, snapshot_id):
        state = self.aws_handler.get_snapshot_data(snapshot_id=snapshot_id)['Snapshots'][0]['State']
        return state

    def delete(self):
        self.aws_handler.delete_volume(self.volume_id)

    def remove_snapshot_tag(self):
        self.aws_handler.remove_volume_tag(self.volume_id, 'Snapshot', 'true')