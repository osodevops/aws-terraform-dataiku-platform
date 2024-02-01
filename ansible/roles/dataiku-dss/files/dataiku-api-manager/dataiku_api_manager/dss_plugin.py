# https://doc.dataiku.com/dss/latest/python-api/plugins.html


class Plugin:
    dss_client: object

    def __init__(self, dss_client):
        self.dss_client = dss_client

    def get_plugin(self, plugin):
        return self.dss_client.get_plugin(plugin)

    def get_installed(self):
        return self.dss_client.list_plugins()

    def install_plugin(self, plugin):
        # If the plugin is already installed don't try and install it again.
        if self.plugin_installed(plugin):
            print("Plugin %s already installed." % (plugin))
            return

        res = self.dss_client.install_plugin_from_store(plugin)

        if not res.wait_for_result()['success']:
            print("Plugin %s failed to install." % (plugin))
            raise Exception
        
        print("Plugin %s installed successfully." % (plugin))

    def plugin_installed(self, plugin):
        # Default to get the installed plugin list, if an alternative array isn't pass in via data.
        rest = [result for result in self.get_installed() if result['id'] == plugin]

        # return true if the plugin has been installed/found.
        if not rest:
            return False

        return True
