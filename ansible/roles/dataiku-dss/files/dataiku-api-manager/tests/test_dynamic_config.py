import json

import pytest


def test_dynamic_config_no_file():
    with pytest.raises(FileNotFoundError):
        dynamic = DynamicConfig("tests/notexist.json")


def test_dynamic_config_malformed_file():
    with pytest.raises(json.JSONDecodeError):
        dynamic = DynamicConfig("tests/dummy_dynamic_config_malformed.json")


def test_dynamic_config():
    dynamic = DynamicConfig("tests/dummy_dynamic_config.json")
    assert dynamic.get('foo') == "bar"
    assert dynamic.get('baz') == ['a', 'b']
    assert dynamic.get('doe') == {'key': 'value'}
    assert dynamic.get('region') == "eu-west-2"


def test_missing_key():
    dynamic = DynamicConfig("tests/dummy_dynamic_config.json")
    with pytest.raises(Exception):
        _ = dynamic.get('nope')
