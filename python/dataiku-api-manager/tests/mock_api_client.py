from tests.common import call_counter
from tests.mock_plugin import MockDssPlugin, MockDssFuture


class MockDssSettings:
    @staticmethod
    def get_raw():
        return {
            "defaultK8sClusterId": "foobar",
            "containerSettings": {
                "kube": ["foo", "bar"]
            },
            "cgroupSettings": {"foo": "bar"}
        }

    @staticmethod
    @call_counter
    def save():
        pass


class MockStatus:
    attached: bool

    def __init__(self, attached):
        self.attached = attached

    def get_raw(self):
        if self.attached:
            return {
                "state": "RUNNING"
            }
        else:
            return {
                "state": "NOTRUNNING"
            }


class MockCluster:
    cluster_id: str
    cluster_type: str
    config: {}
    attached: bool

    def __init__(self, cluster_id, cluster_type, config):
        self.cluster_id = cluster_id
        self.cluster_type = cluster_type
        self.config = config
        self.attached = False

    @call_counter
    def start(self):
        self.attached = True

    def get_status(self):
        return MockStatus(self.attached)


class MockUserClient:
    def __init__(self):
        pass

    @staticmethod
    def get_client_as():
        return MockDssClient()


class MockDssClient:
    fail_plugin_install: bool
    fail_license_check: int
    fail_infrastructure_install: bool

    def __init__(self, fail_plugin_install=False, fail_license_check=0, fail_infrastructure_install = False):
        self.fail_plugin_install = fail_plugin_install
        self.fail_license_check = fail_license_check
        self.fail_infrastructure_install = fail_infrastructure_install

    @staticmethod
    def check_mock():
        return True

    @staticmethod
    def get_plugin(plugin_name):
        return MockDssPlugin(name=plugin_name)

    @staticmethod
    @call_counter
    def list_plugins():
        return ["foo", "bar"]

    @call_counter
    def install_plugin_from_store(self, plugin):
        return MockDssFuture(self.fail_plugin_install)

    @staticmethod
    def get_general_settings():
        return MockDssSettings()

    @staticmethod
    @call_counter
    def create_cluster(cluster_id, cluster_type, config):
        return MockCluster(cluster_id, cluster_type, config)

    def list_clusters(self):
        return [
            {"name": "cluster_exists"}
        ]

    @staticmethod
    @call_counter
    def create_connection(name, connection_type, params, usable_by, allowed_groups):
        pass

    @staticmethod
    @call_counter
    def list_connections():
        return {
            "foo_connection": "true"
        }

    @staticmethod
    def get_user(user):
        return MockUserClient()

    @staticmethod
    @call_counter
    def set_license(license_content):
        pass

    @call_counter
    def get_licensing_status(self):
        if self.fail_license_check == 1:
            return {
                "base": {
                    "expired": True,
                    "hasLicense": True,
                    "valid": True
                }
            }
        if self.fail_license_check == 2:
            return {
                "base": {
                    "expired": False,
                    "hasLicense": False,
                    "valid": False
                }
            }
        return {
            "base": {
                "expired": False,
                "hasLicense": True,
                "valid": True
            }
        }

    def get_apideployer(self):
        return MockApiDeployer(self.fail_infrastructure_install)

    def get_projectdeployer(self):
        return MockProjectDeployer(self.fail_infrastructure_install)


class MockProjectDeployer:
    fail_infrastructure_install: bool

    def __init__(self, fail_infrastructure_install):
        self.fail_infrastructure_install = fail_infrastructure_install

    def get_infra(self, id):
        if self.fail_infrastructure_install:
            return MockIfra("RandomId")
        return MockIfra(id)

    def create_infra(self, id, stage):
        return {
            "id": id,
            "stage": stage
        }


class MockApiDeployer:
    fail_infrastructure_install: bool
    def __init__(self, fail_infrastructure_install):
        self.fail_infrastructure_install = fail_infrastructure_install
    
    def create_infra(self, id, stage, type):
        return {
            "id": id, 
            "stage": stage,
            "type": type
        }

    def status(id):
        return {
            "infraBasicInfo": {
                "id": "infraIdTest134"
            }
        }

    def get(id):
        return {"prePushMode": "ECR"}

    def get_settings():
        return {"prePushMode": "ECR"}

    def get_infra(self, id):
        if self.fail_infrastructure_install:
            return MockIfra("RandomId")
        return MockIfra(id)

class MockIfra:
    infraId: str
    settings: object
    def __init__(self, infraId, settings = {}):
        self.infraId = infraId
        self.settings = settings
        pass

    def get_status(self):
        return self

    def get_raw(self):
        return { 
            "infraBasicInfo": {
                    "id": self.infraId
                }
            } 

    def get_settings(self):
        return MockSettings(self.settings)

class MockSettings:
    settings: object
    def __init__(self, settings = {}):
        self.settings = settings
        pass

    def get_raw(self):
        if not self.settings:
            return {
                "prePushMode": "ECR",
                "k8sNamespace":  "dataiku",
                "baseImageTag":  "baseImageTag123",
                "registryHost": "registryHost123"
            }
        return self.settings

    def save(self):
        pass