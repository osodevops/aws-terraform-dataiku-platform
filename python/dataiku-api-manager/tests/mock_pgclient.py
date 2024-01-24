import re

from tests.common import call_counter


class MockCursor:
    fail: bool

    def __init__(self):
        self.fail = False

    @call_counter
    def execute(self, command):
        if re.search('fail', command):
            self.fail = True

    def fetchone(self):
        if self.fail:
            return None
        return ('success',)

    @staticmethod
    @call_counter
    def close():
        pass


class MockClient:
    def __init__(self):
        pass

    @staticmethod
    def check_mock():
        return True

    @staticmethod
    def cursor():
        return MockCursor()

    @call_counter
    def commit(self):
        pass


def get_mock_client():
    return MockClient()