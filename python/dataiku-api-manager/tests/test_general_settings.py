from unittest import mock

from src.dss_general_settings import GeneralSettings
from tests.mock_api_client import MockDssClient, MockDssSettings
import pytest


def test_generalsettings():
    mock_client = MockDssClient()
    settings_obj = GeneralSettings(mock_client)


@pytest.mark.parametrize("container_type, settings, expected", [
    ('kube', ["foo1", "foo2"], {
            "defaultK8sClusterId": "foobar",
            "containerSettings": {
                "kube": ["foo1", "foo2"]
            },
            "cgroupSettings": {"foo": "bar"}
        }),
    ('kube', [], {
            "defaultK8sClusterId": "foobar",
            "containerSettings": {
                "kube": []
            },
            "cgroupSettings": {"foo": "bar"}
        })
])
@mock.patch('src.general_settings.GeneralSettings._ensure_saved')
def test_update_container(mock_ensure_saved, container_type, settings, expected):
    mock_client = MockDssClient()
    settings_obj = GeneralSettings(mock_client)
    settings_obj.update_container(container_type, settings)

    assert settings_obj.settings_raw == expected
    assert mock_ensure_saved.called


@mock.patch('src.general_settings.GeneralSettings._ensure_saved')
def test_update_default_cluster(mock_ensure_saved):
    mock_client = MockDssClient()
    settings_obj = GeneralSettings(mock_client)

    settings_obj.update_default_cluster('footest')
    assert settings_obj.settings_raw['defaultK8sClusterId'] == 'footest'
    assert mock_ensure_saved.called
    settings_obj.update_default_cluster('')
    assert settings_obj.settings_raw['defaultK8sClusterId'] == ''


@pytest.mark.parametrize("settings, expected", [
    (
        {
            "enabled": True,
            "mlKernels": "cgroupdata"
        },
        {
            "defaultK8sClusterId": "foobar",
            "containerSettings": {
                "kube": ['foo', 'bar']
            },
            'cgroupSettings': {'enabled': True, 'mlKernels': 'cgroupdata'}
        }
    ),
    (
        {},
        {
            "defaultK8sClusterId": "foobar",
            "containerSettings": {
                "kube": ['foo', 'bar']
            },
            'cgroupSettings': {}
        }
    )])
@mock.patch('src.general_settings.GeneralSettings._ensure_saved')
def test_update_cgroups(mock_ensure_saved, settings, expected):
    mock_client = MockDssClient()
    settings_obj = GeneralSettings(mock_client)
    settings_obj.update_cgroups(settings)

    assert settings_obj.settings_raw == expected
    assert mock_ensure_saved.called


def test_ensure_saved():
    mock_client = MockDssClient()
    settings_obj = GeneralSettings(mock_client)

    settings_obj._ensure_saved("defaultK8sClusterId", settings="foobar")
    assert MockDssSettings.save.calls == 1
    MockDssSettings.save.calls = 0

    settings_obj._ensure_saved("containerSettings", "kube", settings=["foo", "bar"])
    assert MockDssSettings.save.calls == 1
    MockDssSettings.save.calls = 0

    with pytest.raises(Exception):
        settings_obj._ensure_saved("containerSettings", "kube", settings=[])
    assert MockDssSettings.save.calls == 1
    MockDssSettings.save.calls = 0

    with pytest.raises(Exception):
        settings_obj._ensure_saved("fuzz", settings=[])
    assert MockDssSettings.save.calls == 1
    MockDssSettings.save.calls = 0