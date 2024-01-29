from dataiku_api_manager.exceptions import ConfiguratorException


class User:
    dss_client: object
    settings: dict
    settings_raw: dict
    user: [object, None]

    def __init__(self, dss_client, user):
        self.dss_client = dss_client
        self.user = None
        if user:
            self.get_user(user)

    def get_user(self, user):
        try:
            self.user = self.dss_client.get_user(user)
            self.settings = self.user.get_settings()
            self.settings_raw = self.settings.get_raw()
        except Exception as e:
            raise ConfiguratorException("Could not retrieve user details from DSS endpoint", e) from None
    
    def set_profile(self, profile):
        if self.profile_saved(profile):
            return print("profile %s already set." % (profile))

        self.settings_raw["userProfile"] = profile
        self.settings.save()

        if self.profile_saved(profile):
            return print("profile %s successfully set." % (profile))
    
    def profile_saved(self, profile):
        if self.settings.get_raw()['userProfile'] == profile:
            return True
        return False

    def property_saved(self, key, value):
        if self.settings.get_raw()[key] == value:
            return True
        return False

    def set_property(self, key, value):
        self.settings_raw[key] = value
        self.settings.save()

        if self.property_saved(key, value):
            return print("property %s successfully set." % (key))