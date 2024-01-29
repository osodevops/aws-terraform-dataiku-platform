import logging

import dataikuapi

from src.dataiku_controller import DataikuController

logger = logging.getLogger(__name__)


def dss_client(func):
    def wrapper(self, *args, **kwargs):
        if not self.dss_client:
            logger.info(f"Authenticating to DSS")
            if not self.dss_auth_settings.get('url', None) or not self.dss_auth_settings.get('api_key', None):
                logger.critical(f"Missing auth parameters, url or api key")
            admin_client = dataikuapi.DSSClient(
                self.dss_auth_settings.get('url', None),
                self.dss_auth_settings.get('api_key', None)
            )
            user = admin_client.get_user(self.dss_auth_settings.get('user', "admin"))
            self.dss_client = user.get_client_as()
        result = func(self, *args, **kwargs)
        return result
    return wrapper


def apideployer_client(func):
    def wrapper(self, *args, **kwargs):
        if not self.apideployer_client:
            self.apideployer_client = self.dss_client.get_apideployer()
        result = func(self, *args, **kwargs)
        return result
    return wrapper


def dss_service_handler(func):
    def wrapper(self, *args, **kwargs):
        if not self.dss_service_handler:
            self.dss_service_handler = DataikuController(dss_path=self.dss_service_settings.get('dss_path'),
                                                         su_user=self.dss_service_settings.get('su_user'))
        result = func(self, *args, **kwargs)
        return result
    return wrapper
