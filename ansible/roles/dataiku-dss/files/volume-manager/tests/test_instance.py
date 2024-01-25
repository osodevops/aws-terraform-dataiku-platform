from unittest import mock

from src.instance import Instance
import responses

from tests.mock_apis import MockAws, MockConfig

from testfixtures import LogCapture


@responses.activate
def test_instance():
    responses.add(responses.GET, "http://169.254.169.254/latest/meta-data/instance-id", status=200, body="foo-123")
    aws_obj = MockAws()
    instance = Instance(aws_obj)

    assert instance.instance_id == "foo-123"


@responses.activate
def test_get_instance_id():
    responses.add(responses.GET, "http://169.254.169.254/latest/meta-data/instance-id", status=200, body="foo-123")
    aws_obj = MockAws()
    instance = Instance(aws_obj)

    instance_id = instance.get_instance_id()
    assert instance_id == "foo-123"


@responses.activate
def test_get_instance_data():
    responses.add(responses.GET, "http://169.254.169.254/latest/meta-data/instance-id", status=200, body="foo-123")
    aws_obj = MockAws()
    instance = Instance(aws_obj)

    response = instance.get_instance_data()
    assert response == {'az': "'eu-west-2", 'instance_id': 'foo-123'}

    response = instance.get_instance_data('instance_id')
    assert response == 'foo-123'


@responses.activate
def test_wait_for_closing_instances():
    responses.add(responses.GET, "http://169.254.169.254/latest/meta-data/instance-id", status=200, body="foo-123")
    aws_obj = MockAws()
    instance = Instance(aws_obj)
    instance.sleep_wait_period = 1

    with LogCapture() as l:
        instance.wait_for_instances(states=['running'], max_attempts=2)
        l.check(('root', 'WARNING', "Waiting for instances in state ['running']"),
                ('root', 'WARNING', "Waiting for instances in state ['running']"),
                ('root', 'WARNING', 'Reached maximum number of retries waiting for instance'))
