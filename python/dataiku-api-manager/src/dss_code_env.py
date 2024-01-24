# https://doc.dataiku.com/dss/latest/python-api/plugins.html


class CodeEnv:
    plugin: object
    dss_client: object
    build_result: dict

    def __init__(self, dss_client, plugin):
        self.dss_client = dss_client
        self.plugin = plugin
        self.build_result = {}

    def build(self, env_name, plugin):
        plugin = self.plugin.get_plugin(plugin)
        future = plugin.create_code_env()
        self.build_result = future.wait_for_result()

        # NB: If the plugin requires Python 3.6 for example, you will use something like:
        # plugin.create_code_env(python_interpreter="PYTHON36")

        # Now the code env is created, but we still need to configure the plugin to use it.
        settings = plugin.get_settings()
        settings.set_code_env(env_name)
        settings.save()

    def build_successful(self):
        for message in self.build_result['messages']['messages']:
            if message['title'] != 'Import succeeded':
                print("Code build failed.")
                raise Exception('Failed to build code environment')

        print("Code environment built successfully.")
        return

    def build_exists(self, env_name, plugin):
        try:
            return env_name == self.plugin.get_plugin(plugin).get_settings().get_raw()['codeEnvName']
        except KeyError:
            return False