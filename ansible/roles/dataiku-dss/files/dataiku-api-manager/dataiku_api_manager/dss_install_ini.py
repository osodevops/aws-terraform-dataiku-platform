import configparser
from dataiku_controller import DataikuController


class InstallIni:
    path: str
    data: dict
    dataiku: DataikuController

    def __init__(self, path, data={}, dataiku_controller=DataikuController()):
        self.path = path
        self.data = data
        self.dataiku = dataiku_controller

    def write_configuration(self):
        data = self.set_configuration()

        self.dataiku.stop_dss_service()

        with open(self.path, 'w') as configfile:
            data.write(configfile)

        self.dataiku.regenerate_config()
        self.dataiku.start_dss_service()

    def set_configuration(self):
        parser = configparser.ConfigParser()
        parser.read(self.path)
        for key, value in self.data.items():
            parser[key] = value

        return parser
