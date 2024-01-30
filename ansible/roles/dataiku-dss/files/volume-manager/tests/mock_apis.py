from datetime import datetime

import botocore.config
from dateutil.tz import tzutc

from src.aws import Aws


class MockAws(Aws):
    empty_snapshots: bool

    def __init__(self, empty_snapshots=False):
        self.empty_snapshots = empty_snapshots
        self.instance_ids = iter({'123', 456})

    @staticmethod
    def get_az_from_instance(instance_id):
        return "'eu-west-2"

    def get_instance_tags(self, instance_id):
        return [
            {
                "Key": "Key1",
                "Value": "Value1"
            },
            {
                "Key": "Key2",
                "Value": "Value2"
            }
        ]

    def get_instance_id(self, states, additional_tags, exclude_id):
        print("Got an instance id")
        try:
            t = next(self.instance_ids)
        except:
            return None
        return t

    def get_snapshot_data(self, search_tags):
        if self.empty_snapshots:
            return {
                "Snapshots": []
            }

        return {
            "Snapshots": [
                {
                    "StartTime": datetime(2020, 1, 1, 1, 1, 1, 950000, tzinfo=tzutc()),
                    "State": "old",
                    "SnapshotId": "123456"
                },
                {
                    "StartTime": datetime(2021, 1, 2, 3, 1, 1, 950000, tzinfo=tzutc()),
                    "State": "new",
                    "SnapshotId": "456789"
                }
            ]
        }

    def get_volume_data(self, az, volume_id="", snapshot_id="", search_tags={}):
        return {'Volumes': [{
            'CreateTime': datetime(2020, 1, 1, 1, 1, 1, 950000, tzinfo=tzutc()),
            'VolumeId': '123456',
            'State': 'pending',
            'AvailabilityZone': 'eu-west-2',
            'SnapshotId': 'someid'
        }]
        }


class MockConfig:
    region = 'eu-west-2'

    # Volume settings
    encrypt_volumes = True
    volume_iops = ""
    kms_key = ""
    volume_type = "gp3"
    volume_size = "40"
    volume_device_name = "/dev/sdb"
    volume_mount_point = "/datafoo"

    boto_config = botocore.config.Config(
        region_name=region,
        signature_version='v4',
        retries={
            'max_attempts': 4,
            'mode': 'standard'
        }
    )
