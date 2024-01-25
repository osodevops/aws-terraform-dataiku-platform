from tests.common import call_counter


class MockDssPlugin:
    fail_build: bool
    name: str

    def __init__(self, fail_build=False, name=""):
        self.fail_build = fail_build
        self.name = name

    @call_counter
    def create_code_env(self):
        return MockDssFuture(self.fail_build)

    @staticmethod
    def get_settings():
        return MockDssSettings()


class MockDssSettings:
    @staticmethod
    @call_counter
    def set_code_env(environment):
        pass

    @staticmethod
    @call_counter
    def save():
        pass


class MockDssFuture:
    fail_build: bool

    def __init__(self, fail_build):
        self.fail_build = fail_build

    def wait_for_result(self):
        if self.fail_build:
            result = {
                "envName": "foo",
                'success': False,
                'messages': {
                    'messages': [
                        {
                            'severity': 'INFO',
                            'isFatal': False,
                            'code': 'INFO_CODEENV_IMPORT_OK',
                            'title': 'Import failed',
                            'details': 'Imported foo as code env bar',
                            'message': 'Import failed: Imported foo as code env bar'
                        }
                    ],
                    'maxSeverity': 'INFO',
                    'anyMessage': True,
                    'success': False,
                    'warning': False,
                    'error': False,
                    'fatal': False
                }
            }
        else:
            result = {
                "envName": "foo",
                'success': True,
                'messages': {
                    'messages': [
                        {
                            'severity': 'INFO',
                            'isFatal': False,
                            'code': 'INFO_CODEENV_IMPORT_OK',
                            'title': 'Import succeeded',
                            'details': 'Imported foo as code env bar',
                            'message': 'Import succeeded: Imported foo as code env bar'
                        }
                    ],
                    'maxSeverity': 'INFO',
                    'anyMessage': True,
                    'success': False,
                    'warning': False,
                    'error': False,
                    'fatal': False
                }
            }

        return result


class MockPlugin:
    mock_dss_plugin: [MockDssPlugin, None]
    fail_build: bool

    def __init__(self, fail_build=False):
        self.mock_dss_plugin = None
        self.fail_build = fail_build

    @staticmethod
    def check_mock():
        return True

    def get_plugin(self, plugin):
        self.mock_dss_plugin = MockDssPlugin(self.fail_build)
        return self.mock_dss_plugin
