class ProjectInfrastructure:
    dss_client: object

    def __init__(self, dss_client):
        self.dss_client = dss_client.get_projectdeployer()

    def create_save_settings(self, id, stage, config={}):
        infra = self.create(id, stage)
        self.save_settings(infra, config) 

    def get(self, id):
        return self.dss_client.get_infra(id)

    def status(self, id):
        try:
            return self.get(id).get_status().get_raw()
        except:
            return False
    
    def exists(self,id):
        if not self.status(id):
            return False
        return self.status(id)['infraBasicInfo']['id'] == id

    def create(self, id, stage):
        if self.exists(id):
            print("Project infrastructure %s already exists." % (id))
            return self.get(id)

        self.dss_client.create_infra(id, stage)

        if self.exists(id):
            print("Project infrastructure %s successfully created." % (id))
            return self.get(id)

        return print("failed to create project infrastructure %s" % (id))

    def save_settings(self, infra={}, config={}):
        if not self.setting_altered(infra, config):
            print("No settings have been altered...")
            return False

        print("Saving project infrastructure settings...")
        settings = infra.get_settings()

        # Save all key/values.
        for (key, value) in config.items():
            settings.get_raw()[key] = value
        settings.save()

        # Check all keys have saved correctly.
        for (key, value) in config.items():
            if infra.get_settings().get_raw()[key] == value:
                print("Project infrastructure %s saved." % (key))
            else:
                print("Project infrastructure %s failed to save." % (key))

    @staticmethod
    def setting_altered(infra={}, config={}):
        settings = infra.get_settings().get_raw()
        for (key, value) in config.items():

            # If the key value doesnt exist and the key isnt in the raw object from Dataiku add the key and value.
            if settings.get(key) != value and key not in infra.get_settings().get_raw():
                settings[key] = value

            # If the key matches the value and the key exists in the get_raw object then infra hasnt changed.
            if settings[key] == value and key in infra.get_settings().get_raw():
                print("Infrastructure %s hasn't changed" % (key))
            else:
                print("Infrastructure %s has been altered." % (key))
                return True
