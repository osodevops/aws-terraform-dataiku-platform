import os
from unittest import mock

import pytest

from json_parser.exceptions import JsonParserException
from json_parser.parser import JsonParser


class JsonTester(JsonParser):
    valid_keys = ["key", "cost", "price", "account", "tenant"]
    valid_sub_categories = ["valid", "invalid"]
    my_sub_category = "valid"


def test_object():
    parser = JsonTester(
        data={"key": "value"},
        use_when=False
    )

    # Getters and setters
    parser['key'] = "new"
    assert parser['key'] == 'new'

    parser['key'] = ["foo", "bar"]
    assert parser['key'] == ["foo", "bar"]

    parser['key'] = True
    assert parser['key'] is True

    parser['key'] = {"foo": "bar"}
    assert parser['key'] == {"foo": "bar"}

    parser['key'] = {"foo": "bar"}
    assert parser['key'] == {"foo": "bar"}

    with pytest.raises(JsonParserException):
        parser['bar'] = {"foo": "bar"}


def test_parse_value():
    parser = JsonTester(
        data={"key": "value"},
        use_when=False
    )

    assert parser._parse_value('foo') == 'foo'
    assert parser._parse_value(["foo", "bar"]) == ["foo", "bar"]
    assert parser._parse_value({"foo": "bar"}) == {"foo": "bar"}
    assert parser._parse_value({"foo": "bar", "backend_provider": "test"}) == "backend_data"
    assert parser._parse_value({"foo": "bar", "sub": {"backend_provider": "test"}}) == {"foo": "bar",
                                                                                        "sub": "backend_data"}
    assert parser._parse_value({"foo": "bar", "sub": {"baz": "meh"}}) == {"foo": "bar", "sub": {"baz": "meh"}}
    assert parser._parse_value({"foo": "bar", "sub": [{"baz": "meh"}]}) == {"foo": "bar", "sub": [{"baz": "meh"}]}


def test_parse_config_when_true():
    parser = JsonTester(
        data={"key": "value"},
        use_when=True,
    )

    assert not parser._parse_config({})
    assert not parser._parse_config({"key": "bar"})  # should return somethinhg?

    test_input = {
        "when": "always",
        "valid": {"bar": "valid"},
        "invalid": {"bar": "invalid"},
        "nonexistent": {"bar": "nonexistent"},
        "bar": "baz"
    }
    expected_output = {
        "bar": "valid",
        "when": "always",
        "nonexistent": {"bar": "nonexistent"}
    }
    assert parser._parse_config(test_input) == expected_output

    test_input = {
        "when": "never",
        "bar": "baz"
    }
    expected_output = {}
    assert parser._parse_config(test_input) == expected_output


def test_parse_config_when_false():
    parser = JsonTester(
        data={"key": "value"},
        use_when=False,
    )

    assert not parser._parse_config({})
    assert parser._parse_config({"key": "bar"}) == {"key": "bar"}
    assert parser._parse_config({"foo": "bar"}) == {"foo": "bar"}

    test_input = {
        "when": "always",
        "valid": {"bar": "valid"},
        "invalid": {"bar": "invalid"},
        "nonexistent": {"bar": "nonexistent"},
        "bar": "baz"
    }
    expected_output = {
        "bar": "valid",
        "when": "always",
        "nonexistent": {"bar": "nonexistent"}
    }
    assert parser._parse_config(test_input) == expected_output

    test_input = {
        "when": "never",
        "bar": "baz"
    }
    expected_output = {
        "bar": "baz",
        "when": "never",
    }
    assert parser._parse_config(test_input) == expected_output


def test_get_backend_data_file():
    parser = JsonTester(
        data={"key": "value"},
        use_when=False,
    )

    assert parser._get_backend_data_file({"filename": "./tests/json_parser/testfile.dat"}) == "somevalue"
    assert parser._get_backend_data_file(
        {"filename": "./tests/json_parser/testfile.dat", "junk": "junk"}) == "somevalue"
    with pytest.raises(JsonParserException):
        assert parser._get_backend_data_file({"junk": "junk"})
    with pytest.raises(JsonParserException):
        assert parser._get_backend_data_file({})
    with pytest.raises(JsonParserException):
        parser._get_backend_data_file({"filename": "./tests/json_parser/notexist.dat"})


def test_get_backend_data_json_file():
    parser = JsonTester(
        data={"key": "value"},
        use_when=False,
    )

    expected_output = "value"
    assert parser._get_backend_data_json_file(
        {"filename": "./tests/json_parser/testfile.json", "key": "key1"}) == expected_output
    assert parser._get_backend_data_json_file(
        {"filename": "./tests/json_parser/testfile.json", "key": "key1", "junk": "junk"}) == expected_output
    with pytest.raises(JsonParserException):
        parser._get_backend_data_json_file(
            {"filename": "./tests/json_parser/testfile.json", "key": "key_notexist"})
    with pytest.raises(JsonParserException):
        parser._get_backend_data_json_file(
            {"filename": "./tests/json_parser/testfile.json"})
    with pytest.raises(JsonParserException):
        parser._get_backend_data_json_file({"key": "key_notexist"})
    with pytest.raises(JsonParserException):
        parser._get_backend_data_json_file({"filename": "./tests/json_parser/notexist.json"})
    with pytest.raises(JsonParserException):
        parser._get_backend_data_json_file({"filename": "./tests/json_parser/testfile_malformed.json"})


def test_get_backend_data_environment():
    parser = JsonTester(
        data={"key": "value"},
        use_when=False,
    )

    os.environ['TEST'] = 'foobar'
    assert parser._get_backend_data_environment({"env_var": "TEST", "default": "some_default"}) == 'foobar'
    assert parser._get_backend_data_environment({"env_var": "TEST"}) == 'foobar'
    assert parser._get_backend_data_environment({"env_var": "TEST", "default": "some_default",
                                                 "junk": "junk"}) == 'foobar'
    assert parser._get_backend_data_environment({"env_var": "TESTNOTEXIST",
                                                 "default": "some_default"}) == 'some_default'
    assert parser._get_backend_data_environment({"env_var": "TESTNOTEXIST",
                                                 "default": ""}) == ''
    assert parser._get_backend_data_environment({"env_var": "TESTNOTEXIST"}) == ''
    assert parser._get_backend_data_environment({"env_var": "TESTNOTEXIST", "junk": "junk",
                                                 "default": "some_default"}) == 'some_default'
    with pytest.raises(JsonParserException):
        parser._get_backend_data_environment({"default": "some_default"})


def test_when_run():
    parser = JsonTester(
        data={"key": "value"},
        use_when=False
    )

    assert parser._when_run(["foo", "bar"])
    assert parser._when_run("")
    assert parser._when_run("always")
    assert parser._when_run("once")
    assert parser._when_run("never")

    parser.use_when = True
    assert not parser._when_run(["foo", "bar"])
    assert parser._when_run(["foo", "bar", "valid"])
    assert not parser._when_run("")

    assert parser._when_run("always")
    assert parser._when_run("once")
    assert not parser._when_run("never")


def test_overall():
    parser = JsonTester(
        data={"key": "value"},
        use_when=True
    )

    os.environ['TEST'] = 'foobar'

    data = {
        "key": {
            "when": "always",
            "endpoint_url": {"backend_provider": "environment", "env_var": "TEST", "default": "http://localhost:11200"},
            "admin_key": {"backend_provider": "test"},
            "foo": "bar"
        },
        "cost": {
            "when": "once",
            "foo": {"backend_provider": "environment", "env_var": "TEST_NOTEXIST"}
        },
        "price": {
            "when": "always",
            "user": {"backend_provider": "file", "filename": "./tests/json_parser/testfile.dat"},
            "other_user": {"backend_provider": "json_file", "filename": "./tests/json_parser/testfile.json",
                           "key": "key2"},
            "profile": "DESIGNER"
        },
        "tenant": {
            "when": "never",
            "user": "thing",
        },
        "account": {
            "when": "always",
            "invalid": {
                "inipath": "/data/dataiku/install.ini",
                "inicontents": {
                    "javaopts": {
                        "foo": "bar"
                    }
                }
            },
            "valid": {
                "inipath": "/data/dataiku/install.ini",
                "inicontents": {
                    "javaopts": {
                        "baz": "lurman"
                    }
                }
            }
        },
        "junk": "junk"
    }

    parser.load_data(data)
    assert parser["key"] == {
        'admin_key': 'backend_data',
         'endpoint_url': 'foobar',
         'foo': 'bar',
         'when': 'always'
    }
    assert parser["cost"] == {'foo': '', 'when': 'once'}
    assert parser["price"] == {
        'other_user': {'subkey': 'subvalue'},
        'profile': 'DESIGNER',
        'user': 'somevalue',
        'when': 'always'
    }
    assert parser["tenant"] == {}
    assert parser["account"] == {
        'inicontents': {'javaopts': {'baz': 'lurman'}},
         'inipath': '/data/dataiku/install.ini',
         'when': 'always'
    }

    with pytest.raises(JsonParserException):
        _ = parser["invalid"]
    with pytest.raises(JsonParserException):
        _ = parser["junk"]
