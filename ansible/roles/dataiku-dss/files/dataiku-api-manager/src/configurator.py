import logging

import dataikuapi

from aws_helper.helper import AwsHelper
from src import wrappers
from src.dss_cluster import Cluster
from src.dss_code_env import CodeEnv
from src.config_generator import ConfigGenerator
from src.dss_connection import Connection
from src.dataiku_controller import DataikuController
from src.dss_general_settings import GeneralSettings
from src.dss_global_variables import GlobalVariables
from src.dss_infrastructure import Infrastructure
from src.dss_install_ini import InstallIni
from src.dss_instance import Instance
from src.dss_license import License
from src.dss_plugin import Plugin
from src.dss_project_infrastructure import ProjectInfrastructure
from src.dss_rds import Rds
from src.dss_user import User

logger = logging.getLogger(__name__)


class Configurator:
    dss_client: [dataikuapi.DSSClient, None]
    apideployer_client: [dataikuapi.dss.apideployer.DSSAPIDeployer, None]
    dss_service_handler: [DataikuController, None]
    dss_auth_settings: dict
    aws_region: str
    aws_client: AwsHelper
    config_generator: ConfigGenerator
    dss_service_settings: dict

    def __init__(self, dss_auth_settings={}, aws_region="", dss_service_settings={}) -> None:
        self.dss_auth_settings = dss_auth_settings
        self.aws_region = aws_region
        self.config_generator = ConfigGenerator()
        self.dss_service_settings = dss_service_settings

    @wrappers.dss_client
    def action_set_admin_password(self, config):
        if not config:
            return
        logger.info("Setting admin password")

        user = User(dss_client=self.dss_client, user=config.get('user', 'admin'))
        user.set_property("password", config.get('password'))

    @wrappers.dss_client
    def action_configure_license(self, config):
        if not config:
            return
        logger.info("Configuring license")

        dss_license = License(client=self.dss_client)
        dss_license.update(config.get('license'))
        dss_license.check_status()

    @wrappers.dss_service_handler
    def action_configure_install_ini(self, config):
        if not config:
            return
        logger.info("Configuring install.ini")

        inicontents = config.get('inicontents')
        install_ini = InstallIni(path=config.get('inipath'), data=inicontents,
                                 dataiku_controller=self.dss_service_handler)
        install_ini.write_configuration()

    @wrappers.dss_service_handler
    @wrappers.dss_client
    def action_configure_rds(self, config):
        if not config:
            return
        logger.info("Configuring RDS")

        rds_config = {}
        for i in ['rds_port', 'rds_endpoint', 'rds_username', 'rds_password', 'rds_database_name', 'rds_schema_name']:
            rds_config[i] = config.get(i)
        rds = Rds(dataiku=self.dss_service_handler, **rds_config)
        rds_force_initialization = config.get("rds_force_db_initialisation")

        config_obj = rds.generate_dss_config()
        gsettings = GeneralSettings(self.dss_client)
        try:
            if gsettings.get('internalDatabase')['connection']['type'] == config_obj['connection']['type'] \
                    and config.get('when') == 'once':
                logger.info("Skipping. RDS is already configured")
                return
        except KeyError:
            pass

        gsettings.update_database(config_obj)

        if not rds.check_database_sync(rds_force_initialization):
            rds.initialise_database()
            rds.migrate_database()

    @wrappers.dss_client
    def action_configure_user_profile(self, config):
        if not config:
            return
        logger.info("Configuring user profile")

        user = User(dss_client=self.dss_client, user=config.get('user', 'admin'))
        user.set_profile(config.get('profile'))

    @wrappers.dss_client
    def action_install_plugins(self, config):
        if not config:
            return
        logger.info("Installing plugins")

        plugin = Plugin(self.dss_client)
        for item in config.get('plugins'):
            logger.info(f"Installing plugin {item['plugin']}")
            plugin.install_plugin(item['plugin'])
            # Check plugin is installed - to be extra safe.
            if not plugin.plugin_installed(item['plugin']):
                logger.critical(f"Plugin {item['plugin']} is not installed or failed to install.")

    @wrappers.dss_client
    def action_build_code_environments(self, config):
        if not config:
            return
        logger.info("Installing code environments for plugins")

        plugin = Plugin(self.dss_client)
        code_env = CodeEnv(self.dss_client, plugin)

        for item in config.get('plugins'):
            if item['build_code_environment'] and not code_env.build_exists(item['code_environment_name'], item['plugin']):
                code_env.build(item['code_environment_name'], item['plugin'])
                code_env.build_successful()
            else:
                logger.info(f"build {item['code_environment_name']} already exists on plugin {item['plugin']}")

    @wrappers.dss_client
    def action_attach_cluster(self, config):
        if not config:
            return
        cluster_id = config.get('cluster_id')
        logger.info(f"Creating DSS EKS cluster {cluster_id}")

        cluster_type = config.get('cluster_type')
        cluster_region = config.get('cluster_region')
        cluster_is_default = config.get('set_as_default_cluster')
        cluster_config = self.config_generator.cluster(region=cluster_region, cluster_id=cluster_id)

        cluster = Cluster(
            dss_client=self.dss_client, cluster_id=cluster_id, cluster_type=cluster_type, cluster_config=cluster_config)
        if cluster.exists(cluster_id):
            logger.info(f"Cluster {cluster_id} already exists")
            return

        cluster.create()
        logger.info(f"Attaching cluster {cluster_id}")
        cluster.attach()
        if cluster.attached():
            logger.info(f"Cluster {cluster_id} attached successfully.")
        else:
            logger.critical(f"Cluster {cluster_id} failed to attach. Check the cluster logs on Dataiku UI.")

        if cluster_is_default:
            logger.info(f"Setting cluster as default")
            settings = GeneralSettings(self.dss_client)
            settings.update_setting_key(key='defaultK8sClusterId', setting=cluster_id)

    @wrappers.dss_client
    def action_set_container_execution(self, config):
        if not config:
            return
        logger.info("Setting container configuration")

        container_type = config.get('container_type')

        setting_config = self.config_generator.containerized_execution(
            base_image=config.get('base_image_name'),
            namespace=config.get('namespace'),
            cluster_id=config.get('cluster_id'),
            registry_host=config.get('registry_host')
        )
        settings = GeneralSettings(self.dss_client)
        settings.update_setting_subkey(key1='containerSettings', key2=container_type, setting=setting_config)

    @wrappers.dss_client
    def action_configure_cgroups(self, config):
        if not config:
            return
        logger.info("Setting cgroups configuration")

        cgroup_config = self.config_generator.cgroups(config.get('cgroup_limits'))

        settings = GeneralSettings(self.dss_client)
        settings.update_setting_key(key='cgroupSettings', setting=cgroup_config)

    @wrappers.dss_client
    def action_create_connections(self, config):
        if not config:
            return
        logger.info("Setting S3 connections")

        connection_hdlr = Connection(self.dss_client)

        for connection in config.get('connections'):
            connection_hdlr.create(
                name=connection.get('name'),
                connection_type=connection.get('type'),
                params=connection.get('params'),
                usable_by=connection.get('usable_by'),
                allowed_groups=connection.get('allowed_groups')
            )
            if connection_hdlr.connected(connection.get('name')):
                logger.info(f"{connection.get('name')} Connected ok")
            else:
                logger.warning(f"{connection.get('name')} NOT connected")

    @wrappers.dss_client
    def action_create_api_infrastructure(self, config):
        if not config:
            return
        logger.info("Creating API infrastructure")

        cluster_id = config.get('cluster_id')
        stage = config.get('stage')
        infra_type = config.get('type')
        namespace = config.get('namespace')
        registry_host = config.get('registry_host')
        image_prefix = config.get('image_name_prefix')
        base_image_name = config.get('base_image_name')

        infra_config = self.config_generator.api_infrastructure(namespace, registry_host, image_prefix, base_image_name)

        infrastructure = Infrastructure(self.dss_client)
        infrastructure.create_save_settings(
            cluster_id, stage,
            infra_type, infra_config)

    @wrappers.dss_client
    def action_create_project_infrastructures(self, config):
        if not config:
            return
        logger.info("Creating Project automation infrastructures")

        for infra in config.get('infrastructures'):
            infra_hdlr = ProjectInfrastructure(self.dss_client)
            infra_config = self.config_generator.project_infrastructure(
                dns_name=infra.get('dns_name'),
                api_key=infra.get('admin_key'),
                trust_certs=infra.get('trust_all_certs')
            )
            infra_hdlr.create_save_settings(id=infra.get('name'), stage=infra.get('stage'), config=infra_config)

    @staticmethod
    def action_create_ssh_keys(config):
        if not config:
            return
        logger.info("Populating SSH keys")

        instance = Instance()
        instance.create_keys(
            key_name=config.get('key_name'),
            home_dir=config.get('home_directory'),
            user=config.get("user"),
            private_key=config.get("private_key"),
            public_key=config.get("public_key")
        )

    # todo: fix this up
    @wrappers.aws_provider
    @wrappers.dss_service_handler
    @wrappers.dss_client
    def action_store_admin_api_token(self):
        ssm_config = {
            'param': "something",
            'value': "something",
            'type': "SecureString",
            'overwrite': True
        }
        self.aws_client.create_or_update_parameter(self.config.automation_admin_key, self.config.token)

    @wrappers.dss_client
    def action_set_global_variables(self, config):
        if not config:
            return
        logger.info("Setting global variables")

        global_variables = GlobalVariables(self.dss_client)
        global_variables.set_variables(config.get("variables"))

    def action_configure_saml(self, config):
        if not config:
            return
        logger.info("Configuring SAML")

        saml_config = self.config_generator.saml(
            enabled=config.get('enabled'),
            saml_idp_metadata=config.get('idp_metadata'),
            entity_id=config.get('saml_entity_id'),
            acs_url=config.get('saml_acs_url')
        )

        settings = GeneralSettings(self.dss_client)
        settings.update_setting_key(key='ssoSettings', setting=saml_config)

