from unittest import mock

from src.dss_rds import Rds
from tests.mock_pgclient import MockClient, get_mock_client, MockCursor


def test_rds_object():
    rds = Rds("foo_database_name", "foo_username", "foo_password", "foo_endpoint", "foo_port", "foo_schema_name")
    assert True


@mock.patch('src.rds.psycopg2.connect', return_value=MockClient())
def test_ensure_client(mock_connect):
    rds = Rds("foo_database_name", "foo_username", "foo_password", "foo_endpoint", "foo_port", "foo_schema_name")
    rds._ensure_client()
    assert rds.rds_client.check_mock()
    rds._ensure_client()
    assert rds.rds_client.check_mock()


@mock.patch('src.rds.psycopg2.connect', return_value=MockClient())
def test_check_schema_exists_no(mock_connect):
    rds = Rds("foo_database_name", "foo_username", "foo_password", "foo_endpoint", "foo_port", "foo_schema_name")
    result = rds._check_schema_exists('fail')
    assert rds.rds_client.check_mock()
    assert not result


@mock.patch('src.rds.psycopg2.connect', return_value=MockClient())
def test_check_schema_exists_yes(mock_connect):
    rds = Rds("foo_database_name", "foo_username", "foo_password", "foo_endpoint", "foo_port", "foo_schema_name")
    result = rds._check_schema_exists('foo')
    assert result


@mock.patch('src.rds.psycopg2.connect', return_value=MockClient())
def test_destroy_schema(mock_connect):
    rds = Rds("foo_database_name", "foo_username", "foo_password", "foo_endpoint", "foo_port", "foo_schema_name")
    MockCursor.execute.calls = 0
    MockClient.commit.calls = 0
    MockCursor.close.calls = 0

    rds._destroy_schema("foo")
    assert MockCursor.execute.calls == 1
    assert MockClient.commit.calls == 1
    assert MockCursor.close.calls == 1


@mock.patch('src.rds.psycopg2.connect', return_value=MockClient())
def test_create_schema(mock_connect):
    rds = Rds("foo_database_name", "foo_username", "foo_password", "foo_endpoint", "foo_port", "foo_schema_name")
    MockCursor.execute.calls = 0
    MockClient.commit.calls = 0
    MockCursor.close.calls = 0

    rds._create_schema("foo_schema", "foouser")
    assert MockCursor.execute.calls == 1
    assert MockClient.commit.calls == 1
    assert MockCursor.close.calls == 1
