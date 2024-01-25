from datetime import datetime

from dateutil.tz import tzutc

from src.snapshot import Snapshot
from tests.mock_apis import MockAws


def test_snapshot():
    aws_obj = MockAws()
    snapshot = Snapshot(aws_obj)
    assert snapshot.state == 'new'


def test_get_snapshot_data():
    aws_obj = MockAws()
    snapshot = Snapshot(aws_obj)

    assert snapshot.get_snapshot_data() == {
        'creation_date': datetime(2021, 1, 2, 3, 1, 1, 950000, tzinfo=tzutc()),
        'exists': True,
        'snapshot_id': '456789',
        'state': 'new'
    }

    assert snapshot.get_snapshot_data('state') == 'new'


def test_snapshot_exists():
    aws_obj = MockAws()
    snapshot = Snapshot(aws_obj)

    assert snapshot.exists()

    aws_obj = MockAws(empty_snapshots=True)
    snapshot = Snapshot(aws_obj)

    assert not snapshot.exists()
