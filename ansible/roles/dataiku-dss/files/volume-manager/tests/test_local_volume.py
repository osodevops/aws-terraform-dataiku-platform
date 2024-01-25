from src.local_volume import LocalVolume
from tests.mock_apis import MockConfig


def test_local_volume_obj():
    config = MockConfig()
    volume_data = {
        'exists': False,
        'volume_id': "",
        'creation_date': None,
        'blank_filesystem': True,
        'az': ""
    }

    volume_obj = LocalVolume(volume_data, config)

    assert volume_obj.blank()
