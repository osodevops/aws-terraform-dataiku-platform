import logging

from config import Config
from configurator import Configurator
from system_config import SystemConfig

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def main():

    system_config = SystemConfig(
        aws_region="eu-west-2",
        node_type="design",
        system_json_file="./system-settings.json",
        # dss_config_file="",
        # dss_config_s3_bucket="",
        # dss_config_s3_key="",
        # dss_config_s3_bucket_tag="ConfigS3Bucket",
        # dss_config_s3_key_tag="ConfigS3Key",
        dss_node_type_tag="DssType"
    )

    system_config.load_system_config()
    dss_config = Config(
        aws_region=system_config.aws_settings["aws_region"],
        sub_categories=['api', 'design', 'automation', 'deployer'],
        my_category=system_config.node_type
    )
    dss_config.load_data(system_config.get_config_data())
    dss_config.initialize_backend_settings()

    dss_config.get_dss_auth_settings()

    dss_auth_settings = {
        "url": dss_config['dss']['endpoint_url'],
        "api_key": dss_config['dss']['admin_key'],
        "user": dss_config['dss']['admin_user']
    }

    dss_service_settings = {
        "dss_path": f"{dss_config['dss']['deployment_path']}/bin",
        "su_user": dss_config["dss"]["os_user"]
    }

    configurator = Configurator(
        dss_auth_settings=dss_auth_settings,
        aws_region=system_config.aws_settings["aws_region"],
        dss_service_settings=dss_service_settings
    )

    if system_config.node_type == 'automation':
        configurator.action_set_admin_password(dss_config['set_admin_password'])
        configurator.action_configure_license(dss_config['update_license'])
        configurator.action_configure_install_ini(dss_config['install_ini_settings'])
        configurator.action_configure_user_profile(dss_config['set_user_profile'])
        configurator.action_configure_cgroups(dss_config['cgroups'])
        configurator.action_create_ssh_keys(dss_config['populate_ssh_keys'])
        configurator.action_configure_saml(dss_config['saml'])
        configurator.action_store_admin_api_token(f"dss/{system_config.node_type}/automation/api_key")
        configurator.action_create_connections(dss_config['connections'])
        configurator.action_set_global_variables(dss_config['global_variables'])
        configurator.action_docker_pull()

    if system_config.node_type == 'design':
        configurator.action_set_admin_password(dss_config['set_admin_password'])
        configurator.action_configure_license(dss_config['update_license'])
        configurator.action_configure_install_ini(dss_config['install_ini_settings'])
        configurator.action_configure_user_profile(dss_config['set_user_profile'])
        configurator.action_configure_cgroups(dss_config['cgroups'])
        configurator.action_create_ssh_keys(dss_config['populate_ssh_keys'])
        configurator.action_configure_saml(dss_config['saml'])
        configurator.action_install_plugins(dss_config['plugins'])
        configurator.action_build_code_environments(dss_config['plugins'])
        configurator.action_attach_cluster(dss_config['eks_cluster'])
        configurator.action_set_container_execution(dss_config['containerized_execution'])
        configurator.action_create_connections(dss_config['connections'])
        configurator.action_create_api_infrastructure(dss_config['api_infrastructure'])
        configurator.action_set_global_variables(dss_config['global_variables'])
        configurator.action_create_project_infrastructures(dss_config['project_infrastructures'])

    if system_config.node_type == 'api':
        configurator.action_store_admin_api_token()

    if system_config.node_type == 'deployer':
        configurator.action_set_admin_password(dss_config['set_admin_password'])
        configurator.action_configure_license(dss_config['update_license'])
        configurator.action_configure_install_ini(dss_config['install_ini_settings'])
        configurator.action_configure_user_profile(dss_config['set_user_profile'])
        configurator.action_configure_cgroups(dss_config['cgroups'])
        configurator.action_create_ssh_keys(dss_config['populate_ssh_keys'])
        configurator.action_configure_saml(dss_config['saml'])
        configurator.action_store_admin_api_token()

if __name__ == "__main__":
    # execute only if run as a script
    main()
