from datetime import datetime
from unittest import mock

from dateutil.tz import tzutc

from src.volume import Volume
from tests.mock_apis import MockAws

mock_event_data = {
    "instance_id": "123456",
    "az": "eu-west-2"
}

mock_volume = {
    'CreateTime': datetime(2020, 1, 1, 1, 1, 1, 950000, tzinfo=tzutc()),
    'VolumeId': '123456',
    'State': 'pending',
    'AvailabilityZone': 'eu-west-2',
    'SnapshotId': 'testsnapshotid'
}

mock_volume_younger = {
    'CreateTime': datetime(2019, 1, 5, 6, 2, 1, 950000, tzinfo=tzutc()),
    'VolumeId': '123456',
    'State': 'pending',
    'AvailabilityZone': 'eu-west-2'
}

mock_volume_youngest = {
    'CreateTime': datetime(2018, 2, 3, 4, 5, 1, 950000, tzinfo=tzutc()),
    'VolumeId': '123456',
    'State': 'pending',
    'AvailabilityZone': 'eu-west-2'
}


def test_volume():
    aws_obj = MockAws()
    _ = Volume(mock_event_data, aws_obj)
    assert True


@mock.patch('src.volume.Volume._get_latest_volume', autospec=True, return_value=mock_volume)
def test_get_volumes_exists(mock_get_latest_volume):
    aws_obj = MockAws()
    volume_obj = Volume(mock_event_data, aws_obj)
    volume_obj.get_volume({}, "wef123")

    assert volume_obj.creation_date == mock_volume['CreateTime']
    assert volume_obj.volume_id == mock_volume['VolumeId']
    assert volume_obj.state == mock_volume['State']
    assert volume_obj.az == mock_volume['AvailabilityZone']
    assert volume_obj.snapshot_id == mock_volume['SnapshotId']
    assert volume_obj.vol_exists


@mock.patch('src.volume.Volume._get_latest_volume', autospec=True, return_value={})
def test_get_volumes_no_data(mock_get_latest_volume):
    aws_obj = MockAws()
    volume_obj = Volume(mock_event_data, aws_obj)
    volume_obj.get_volume({}, "wef123")

    assert not volume_obj.creation_date
    assert not volume_obj.volume_id
    assert not volume_obj.state
    assert not volume_obj.vol_exists
    assert not volume_obj.snapshot_id


def test_get_latest_volume():
    aws_obj = MockAws()
    volume_obj = Volume(mock_event_data, aws_obj)
    volume_obj.get_volume({}, "wef123")
    data = [
        mock_volume_younger,
        mock_volume,
        mock_volume_youngest
    ]
    selected = volume_obj._get_latest_volume(data)

    assert selected == mock_volume


def test_get_latest_volume_no_data():
    aws_obj = MockAws()
    volume_obj = Volume(mock_event_data, aws_obj)
    selected = volume_obj._get_latest_volume({})

    assert not selected


@mock.patch('src.volume.Volume._get_latest_volume', autospec=True, return_value=mock_volume)
def test_get_volume_data(mock_get_latest_volume):
    aws_obj = MockAws()
    volume_obj = Volume(mock_event_data, aws_obj)
    volume_obj.get_volume({}, "wef123")

    assert volume_obj.get_volume_data() == {
        'exists': True,
        'volume_id': mock_volume['VolumeId'],
        'creation_date': mock_volume['CreateTime'],
        'blank_filesystem': False,
        'az': mock_volume['AvailabilityZone']
    }

    assert volume_obj.get_volume_data(key="exists")
