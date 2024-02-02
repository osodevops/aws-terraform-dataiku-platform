#!/bin/bash

#log output from this user_data script
exec > >(tee /var/log/user-data.log|logger -t user-data ) 2>&1

echo '${api_dynamic_settings_json}' > /opt/dataiku-python/dataiku_api_manager/dynamic-settings.json
chown dataiku:dataiku /opt/dataiku-python/dataiku_api_manager/dynamic-settings.json
chmod 600 /opt/dataiku-python/dataiku_api_manager/dynamic-settings.json

echo '${system_settings_json}' > /opt/dataiku-python/dataiku_api_manager/system-settings.json
chown dataiku:dataiku /opt/dataiku-python/dataiku_api_manager/system-settings.json
chmod 600 /opt/dataiku-python/dataiku_api_manager/system-settings.json

echo '${volume_dynamic_settings_json}' > /opt/dataiku-python/volume_manager/dynamic-settings.json
chown dataiku:dataiku /opt/dataiku-python/volume_manager/dynamic-settings.json
chmod 600 /opt/dataiku-python/volume_manager/dynamic-settings.json
