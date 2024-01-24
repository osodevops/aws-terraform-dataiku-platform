
from unittest import mock

import pytest

from src.dss_plugin import Plugin
from tests.mock_api_client import MockDssClient


def test_plugin_class():
    mock_client = MockDssClient()
    plugin = Plugin(mock_client)

    assert plugin.dss_client == mock_client


def test_get_plugin():
    mock_client = MockDssClient()
    plugin = Plugin(mock_client)

    dss_plugin = plugin.get_plugin("foo")

    assert dss_plugin.name == "foo"


def test_get_installed():
    mock_client = MockDssClient()
    plugin = Plugin(mock_client)

    plugin_list = plugin.get_installed()
    assert plugin_list == ["foo", "bar"]


@mock.patch('src.plugin.Plugin.plugin_installed', return_value=True)
def test_install_plugin_plugin_installed(mock_plugin_installed):
    mock_client = MockDssClient()
    plugin = Plugin(mock_client)

    plugin.install_plugin("foo")
    assert MockDssClient.install_plugin_from_store.calls == 0


@mock.patch('src.plugin.Plugin.plugin_installed', return_value=False)
def test_install_plugin_failure(mock_plugin_installed):
    mock_client = MockDssClient(fail_plugin_install=True)
    plugin = Plugin(mock_client)

    with pytest.raises(Exception):
        plugin.install_plugin("foo")

    assert MockDssClient.install_plugin_from_store.calls == 1
    MockDssClient.install_plugin_from_store.calls = 0


@mock.patch('src.plugin.Plugin.plugin_installed', return_value=False)
def test_install_plugin_success(mock_plugin_installed):
    mock_client = MockDssClient(fail_plugin_install=False)
    plugin = Plugin(mock_client)

    plugin.install_plugin("foo")

    assert MockDssClient.install_plugin_from_store.calls == 1
    MockDssClient.install_plugin_from_store.calls = 0


@mock.patch('src.plugin.Plugin.get_installed', return_value=[{"id": "foobar"}])
def test_plusing_installed_true(mock_get_installed):
    mock_client = MockDssClient(fail_plugin_install=False)
    plugin = Plugin(mock_client)

    result = plugin.plugin_installed('foobar')
    assert result


@mock.patch('src.plugin.Plugin.get_installed', return_value=[{"id": "foobar"}])
def test_plusing_installed_false(mock_get_installed):
    mock_client = MockDssClient(fail_plugin_install=False)
    plugin = Plugin(mock_client)

    result = plugin.plugin_installed('foobar2')
    assert not result