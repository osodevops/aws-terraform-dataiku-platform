import logging
import time
from datetime import datetime

from dateutil.tz import tzutc

from aws import Aws


class Volume:
    vol_exists: bool
    creation_date: [datetime, None]
    volume_id: str
    instance_id: str
    aws_handler: Aws
    state: str
    sleep_wait_period: int = 30
    blank_fs: bool
    az: str
    tags: dict
    snapshot_id: str

    def __init__(self, event_data: dict, aws_handler: Aws):
        self.vol_exists = False
        self.volume_id = ""
        self.creation_date = None
        self.aws_handler = aws_handler
        self.state = ""
        self.blank_fs = False
        self.az = event_data['az']
        self.tags = {}
        self.instance_id = event_data['instance_id']
        self.snapshot_id = ""

    def get_volume(self, search_tag_set, snapshot_id, volume_id=""):
        params = {
            'az': self.az,
        }
        if search_tag_set:
            params['search_tags'] = search_tag_set
        if snapshot_id:
            params['snapshot_id'] = snapshot_id
        if volume_id:
            params['volume_id'] = volume_id
        volume_list = self.aws_handler.get_volume_data(**params)
        if volume_list:
            volume = self._get_latest_volume(volume_list['Volumes'])
            if volume:
                self.vol_exists = True
                self.creation_date = volume['CreateTime']
                self.volume_id = volume['VolumeId']
                self.state = volume['State']
                self.az = volume['AvailabilityZone']
                self.snapshot_id = volume['SnapshotId']
                return True
        return False

    @staticmethod
    def _get_latest_volume(data):
        start_date = datetime(2001, 1, 1, 1, 1, 1, 950000, tzinfo=tzutc())
        selected = {}
        for record in data:
            if record['CreateTime'] > start_date:
                start_date = record['CreateTime']
                selected = record
        return selected

    def get_volume_data(self, key=False):
        dataset = {
            'exists': self.vol_exists,
            'volume_id': self.volume_id,
            'creation_date': self.creation_date,
            'blank_filesystem': self.blank_fs,
            'az': self.az
        }

        if key:
            return dataset[key]

        return dataset

    def exists(self):
        return self.vol_exists

    def delete(self):
        if not self.volume_id:
            logging.warning('Attempted to remove volume by non-existent volume id')
        self.aws_handler.delete_volume(self.volume_id)

    def create_volume(self, create_tag_set: dict, snapshot_id: str = ""):
        if snapshot_id:
            volume_id = self.aws_handler.create_volume_from_snapshot(
                az=self.az,
                snapshot_id=snapshot_id,
                instance_id=self.instance_id,
                tags=create_tag_set
            )
        else:
            volume_id = self.aws_handler.create_blank_volume(
                az=self.az,
                instance_id=self.instance_id,
                tags=create_tag_set
            )
            self.blank_fs = True
        self._get_volumes(self.az, volume_id)
        logging.info(f"Volume id is {self.volume_id}")

        self._wait_for_pending()

    def _wait_for_pending(self):
        while self.aws_handler.get_volume_data(az=self.az,
                                               volume_id=self.volume_id)['Volumes'][0]['State'] != 'available':
            logging.warning('Waiting for Volume to create')
            time.sleep(self.sleep_wait_period)
            self.state = 'available'

    def attach(self, instance_data):
        if self._get_attachment_state() == 'attached':
            logging.info('Volume is already attached')
            return
        if self._get_attachment_state() == 'attaching':
            logging.info('Waiting for volume to attach')
            self._wait_for_pending_attachment()
            return
        logging.debug('Attaching volume')
        self.aws_handler.attach_volume(instance_id=instance_data['instance_id'], volume_id=self.volume_id)
        self._wait_for_pending_attachment()

    def _wait_for_pending_attachment(self):
        while self._get_attachment_state() != 'attached':
            logging.info('Waiting for Volume to attach')
            time.sleep(self.sleep_wait_period)

    def _get_attachment_state(self):
        data = self.aws_handler.get_volume_data(az=self.az, volume_id=self.volume_id)['Volumes'][0]
        if data.get('Attachments', False):
            return data['Attachments'][0]['State']

    def is_attached(self):
        if self._get_attachment_state() == 'attached':
            logging.info('Volume is already attached')
            return True
        return False
