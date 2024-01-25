import pytest

from src.dss_code_env import CodeEnv
from tests.mock_api_client import MockDssClient
from tests.mock_plugin import MockPlugin, MockDssPlugin, MockDssSettings


def test_codeenv_class():
    mock_client = MockDssClient()
    mock_plugin = MockPlugin()

    code_env = CodeEnv(mock_client, mock_plugin)
    assert code_env.dss_client == mock_client
    assert code_env.plugin == mock_plugin
    assert code_env.build_result == {}


def test_build():
    mock_client = MockDssClient()
    mock_plugin = MockPlugin()
    code_env = CodeEnv(mock_client, mock_plugin)

    plugin_to_install = "test-plugin"
    code_env.build("foo_environment", plugin_to_install)

    assert MockDssPlugin.create_code_env.calls == 1
    assert MockDssSettings.set_code_env.calls == 1
    assert MockDssSettings.save.calls == 1
    MockDssPlugin.create_code_env.calls = 1
    MockDssSettings.set_code_env.calls = 1
    MockDssSettings.save.calls = 1


def test_build_successful_success():
    mock_client = MockDssClient()
    mock_plugin = MockPlugin()
    code_env = CodeEnv(mock_client, mock_plugin)

    plugin_to_install = "test-plugin"
    code_env.build("foo_environment", plugin_to_install)

    code_env.build_successful()
    assert True


def test_build_successful_failure():
    mock_client = MockDssClient()
    mock_plugin = MockPlugin(fail_build=True)
    code_env = CodeEnv(mock_client, mock_plugin)

    plugin_to_install = "test-plugin"
    code_env.build("foo_environment", plugin_to_install)

    with pytest.raises(Exception):
        code_env.build_successful()
