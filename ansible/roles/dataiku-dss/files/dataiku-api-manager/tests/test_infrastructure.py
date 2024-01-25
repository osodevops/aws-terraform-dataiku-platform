import pytest
from unittest import mock
from mock_api_client import MockIfra
from src.dss_infrastructure import Infrastructure
from tests.mock_api_client import MockDssClient


def test_infrastructure_class():
    mock_client = MockDssClient(False, 0, True)
    infrastructure = Infrastructure(mock_client)
    assert type(infrastructure.dss_client) is type(mock_client.get_apideployer())


def test_infrastructure_exists(capfd):
    mock_client = MockDssClient(False, 0, False)
    infrastructure = Infrastructure(mock_client)
    infrastructure.create("RandomId", "Test", "K8S")
    out, err = capfd.readouterr()
    assert out == "infrastructure RandomId already exists.\n"


def test_infrastructure_failed_to_create(capfd):
    mock_client = MockDssClient(False, 0, True)
    infrastructure = Infrastructure(mock_client)
    infrastructure.create("infraIdTest1234", "Test", "K8S")
    out, err = capfd.readouterr()
    assert out == "failed to create infrastructure infraIdTest1234\n"


def test_create_infrastructure():
    mock_client = MockDssClient(False, 0, False)
    infrastructure = Infrastructure(mock_client)
    infrastructure.create("infraTestNewlyCreated", "Test", "K8S")

    mock_client = MockDssClient(False, 0, True)
    assert "infraTestNewlyCreated" == infrastructure.status("infraTestNewlyCreated")["infraBasicInfo"]["id"]


def test_successful_get():
    mock_client = MockDssClient(False, 0, False)
    infrastructure = Infrastructure(mock_client)
    assert infrastructure.get("test").get_raw()["infraBasicInfo"]["id"] == MockIfra("test").get_raw()["infraBasicInfo"]["id"]


def test_failed_get():
    mock_client = MockDssClient(False, 0, False)
    infrastructure = Infrastructure(mock_client)
    assert infrastructure.get("test").get_raw()["infraBasicInfo"]["id"] != MockIfra("failtest").get_raw()["infraBasicInfo"]["id"]


def test_status():
    mock_client = MockDssClient(False, 0, False)
    infrastructure = Infrastructure(mock_client)
    assert infrastructure.status("test") == {'infraBasicInfo': {'id': 'test'}}


def test_failed_status():
    mock_client = MockDssClient(False, 0, False)
    infrastructure = Infrastructure(mock_client)
    assert infrastructure.status("test2") != {'infraBasicInfo': {'id': 'test'}}

def test_save_settings_havent_changed(capfd):
    mock_client = MockDssClient(False, 0, False)
    infrastructure = Infrastructure(mock_client)
    data = {
        "prePushMode": "ECR",
        "k8sNamespace":  "dataiku",
        "baseImageTag":  "baseImageTag123",
        "registryHost": "registryHost123"
    }
    infrastructure.create_save_settings("infraIdTest134", "Test", "K8S", data)

    mock = MockIfra("infraIdTest134")
    mock.get_settings().get_raw() == data

def test_save_setting_have_changed(capfd):
    mock_client = MockDssClient(False, 0, False)
    infrastructure = Infrastructure(mock_client)
    data = {
        "prePushMode": "ECR",
        "k8sNamespace":  "dataiku",
        "baseImageTag":  "changed",
        "registryHost": "registryHost123"
    }

    infrastructure.create_save_settings("infraIdTest134", "Test", "K8S",  data)
    mock = MockIfra("infraIdTest134", data)
    assert mock.get_settings().get_raw() == data

def test_save_setting_failed(capfd):
    mock_client = MockDssClient(False, 0, False)
    infrastructure = Infrastructure(mock_client)
    data = {
        "prePushMode": "ECR",
        "k8sNamespace":  "dataiku",
        "baseImageTag":  "changed",
        "registryHost": "registryHost123"
    }

    infrastructure.create_save_settings("infraIdTest134", "Test", "K8S")
    mock = MockIfra("infraIdTest134")
    assert mock.get_settings().get_raw() != data