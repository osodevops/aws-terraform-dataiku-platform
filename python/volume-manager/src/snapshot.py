import logging

import time
from datetime import datetime

from dateutil.tz import tzutc

from aws import Aws


class Snapshot:
    snap_exists: bool
    state: str
    creation_date: datetime
    snapshot_id: str
    aws_handler: Aws
    sleep_wait_period: int = 30
    tags: dict

    def __init__(self, aws_handler: Aws, tags={}):
        self.snap_exists = False
        self.snapshot_id = ""
        self.state = ""
        self.tags = tags
        self.aws_handler = aws_handler
        self.creation_date = datetime(2020, 1, 1, 1, 1, 1, 950000, tzinfo=tzutc())
        snapshot_list = self.aws_handler.get_snapshot_data(search_tags=tags)
        if snapshot_list:
            snapshot = self._get_latest_snapshot(snapshot_list['Snapshots'])
            if snapshot:
                self.state = snapshot['State']
                self.creation_date = snapshot['StartTime']
                self.snap_exists = True
                self.snapshot_id = snapshot['SnapshotId']

    @staticmethod
    def _get_latest_snapshot(data):
        start_date = datetime(2020, 1, 1, 1, 1, 1, 950000, tzinfo=tzutc())
        selected = {}
        for record in data:
            if record['StartTime'] > start_date:
                start_date = record['StartTime']
                selected = record
        return selected

    def get_snapshot_data(self, key=False):
        dataset = {
            'exists': self.snap_exists,
            'snapshot_id': self.snapshot_id,
            'state': self.state,
            'creation_date': self.creation_date
        }

        if key:
            return dataset[key]

        return dataset

    def exists(self):
        return self.snap_exists

    def wait_for_pending(self):
        while self.state == 'pending':
            logging.warning('Waiting for snapshot to complete')
            time.sleep(self.sleep_wait_period)
            snapshot = self.aws_handler.get_snapshot_data(self.snapshot_id)['Snapshots'][0]
            self.state = snapshot['State']
