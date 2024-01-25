class GeneralSettings:
    dss_client: object
    settings: object
    settings_raw: dict

    def __init__(self, dss_client):
        self.dss_client = dss_client
        self._get_settings()

    def _get_settings(self):
        self.settings = self.dss_client.get_general_settings()
        self.settings_raw = self.settings.get_raw()

    def get(self, item):
        return self.settings_raw.get(item)

    def update_setting_key(self, key, setting):
        if self.settings_raw.get(key) != setting:
            self.settings_raw[key] = setting
            self._ensure_saved(key, settings=setting)

    def update_setting_subkey(self, key1: str, key2: str, setting):
        if self.settings_raw[key1][key2] != setting:
            self.settings_raw[key1][key2] = setting
            self._ensure_saved(key1, key2, settings=setting)

    def update_database(self, settings=[]):
        print("Saving database general settings...")
        self.settings_raw["internalDatabase"] = settings
        self._ensure_saved("internalDatabase", "connection", "type", settings=settings['connection']['type'])

    def _parse_setting(self, actual, desired):
        if isinstance(desired, (float, int, str, tuple, type(None))):
            if actual != desired:
                raise Exception(f"Setting {desired} failed to save.")
        try:
            if isinstance(desired, list):
                for index in range(0, len(desired)):
                    self._parse_setting(actual[index], desired[index])
            if isinstance(desired, dict):
                for key in desired.keys():
                    self._parse_setting(actual[key], desired[key])
        except (KeyError, IndexError):
            raise Exception(f"Setting {desired} failed to save.")

    def _ensure_saved(self, *args, settings):
        # This function takes a series of arguments that represent keys in the settings tree, plus a settings value
        # We then re-read the settings from the dataiku api and verify the data is the same as 'settings'
        self.settings.save()
        self._get_settings()
        verify = self.settings_raw

        for arg in args:
            verify = verify[arg]

        self._parse_setting(verify, settings)
