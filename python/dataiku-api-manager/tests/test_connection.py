from unittest import mock

import pytest

from src.dss_connection import Connection
from tests.mock_api_client import MockDssClient


def test_connection():
    mock_client = MockDssClient()
    connection_obj = Connection(mock_client)
    assert True


@mock.patch('src.connection.Connection.connected', return_value=True)
def test_create_already_exists(mock_connected):
    mock_client = MockDssClient()
    connection_obj = Connection(mock_client)

    connection_obj.create()
    assert True


@mock.patch('src.connection.Connection.connected', return_value=False)
def test_create_failure(mock_connected):
    mock_client = MockDssClient()
    connection_obj = Connection(mock_client)

    with pytest.raises(Exception):
        connection_obj.create()
    assert MockDssClient.create_connection.calls == 1
    MockDssClient.create_connection.calls = 0


@mock.patch('src.connection.Connection.connected', side_effect=[False, True])
def test_create_success(mock_connected):
    mock_client = MockDssClient()
    connection_obj = Connection(mock_client)

    connection_obj.create()
    assert MockDssClient.create_connection.calls == 1
    MockDssClient.create_connection.calls = 0


def test_list():
    mock_client = MockDssClient()
    connection_obj = Connection(mock_client)

    assert connection_obj.list() == {"foo_connection": "true"}
    assert MockDssClient.list_connections.calls == 1
    MockDssClient.list_connections.calls = 0


def test_connected_success():
    mock_client = MockDssClient()
    connection_obj = Connection(mock_client)

    assert connection_obj.connected("foo_connection") == "true"
    assert MockDssClient.list_connections.calls == 1
    MockDssClient.list_connections.calls = 0


def test_connected_failure():
    mock_client = MockDssClient()
    connection_obj = Connection(mock_client)

    assert not connection_obj.connected("bar_connection")
    assert MockDssClient.list_connections.calls == 1
    MockDssClient.list_connections.calls = 0
