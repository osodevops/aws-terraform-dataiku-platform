import pytest

from src.dss_license import License
from tests.mock_api_client import MockDssClient


def test_license():
    mock_client = MockDssClient()
    license_obj = License(mock_client, 'tests/dummy_license.txt')

    assert True


def test_update_no_file():
    mock_client = MockDssClient()
    license_obj = License(mock_client, 'tests/notexist.txt')

    with pytest.raises(FileNotFoundError):
        license_obj.update()


def test_update_success():
    mock_client = MockDssClient()
    license_obj = License(mock_client, 'tests/dummy_license.txt')

    license_obj.update()

    assert MockDssClient.set_license.calls == 1
    MockDssClient.set_license.calls = 0


def test_check_status_success():
    mock_client = MockDssClient()
    license_obj = License(mock_client, 'tests/dummy_license.txt')

    license_obj.check_status()
    assert MockDssClient.get_licensing_status.calls == 1
    MockDssClient.get_licensing_status.calls = 0


def test_check_status_failure_expired():
    mock_client = MockDssClient(fail_license_check=1)
    license_obj = License(mock_client, 'tests/dummy_license.txt')

    with pytest.raises(Exception):
        license_obj.check_status()


def test_check_status_failure_invalid():
    mock_client = MockDssClient(fail_license_check=2)
    license_obj = License(mock_client, 'tests/dummy_license.txt')

    with pytest.raises(Exception):
        license_obj.check_status()
