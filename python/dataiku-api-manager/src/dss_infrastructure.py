# https://doc.dataiku.com/dss/latest/python-api/api-services.html?highlight=infra#dataikuapi.dss.apideployer.DSSAPIDeployer.create_infra


class Infrastructure:
    dss_client: object

    def __init__(self, dss_client):
        self.dss_client = dss_client.get_apideployer()

    def create_save_settings(self, id, stage, type, config = {}):
        infra = self.create(id, stage, type)
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

    def create(self, id, stage, type):
        if self.exists(id):
            print("infrastructure %s already exists." % (id))
            return self.get(id)

        self.dss_client.create_infra(id, stage, type)

        if self.exists(id):
            print("infrastructure %s successfully created." % (id))
            return self.get(id)

        return print("failed to create infrastructure %s" % (id))
            
    def save_settings(self, infra={}, config={}):
        if not self.setting_altered(infra, config):
            print("No settings have been altered...")
            return False

        print("Saving infrastructure settings...")
        settings = infra.get_settings()

        # Save all key/values.
        for (key, value) in config.items():
            settings.get_raw()[key] = value
        settings.save()

        # Check all keys have saved correctly.
        for (key, value) in config.items():
            if  infra.get_settings().get_raw()[key] == value:
                print("Infrastructure %s saved." % (key))
            else:
                print("Infrastructure %s failed to save." % (key))

    @staticmethod
    def setting_altered(infra={}, config={}):
        for (key, value) in config.items():
            if  infra.get_settings().get_raw()[key] == value:
                print("Infrastructure %s hasn't changed" % (key))
            else:
                print("Infrastructure %s has been altered." % (key))
                return True
    