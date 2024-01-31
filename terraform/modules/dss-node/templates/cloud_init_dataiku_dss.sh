#!/bin/bash

#log output from this user_data script
exec > >(tee /var/log/user-data.log|logger -t user-data ) 2>&1

echo '${api_dynamic_settings_json}' > /opt/dataiku-python/dataiku-configurator/dynamic-settings.json
chown dataiku:dataiku /opt/dataiku-python/dataiku-configurator/dynamic-settings.json
chmod 600 /opt/dataiku-python/dataiku-configurator/dynamic-settings.json

echo '${system_settings_json}' > /opt/dataiku-python/dataiku-configurator/system-settings.json
chown dataiku:dataiku /opt/dataiku-python/dataiku-configurator/system-settings.json
chmod 600 /opt/dataiku-python/dataiku-configurator/system-settings.json

echo '${volume_dynamic_settings_json}' > /opt/dataiku-python/volume-manager/dynamic-settings.json
chown dataiku:dataiku /opt/dataiku-python/volume-manager/dynamic-settings.json
chmod 600 /opt/dataiku-python/volume-manager/dynamic-settings.json
