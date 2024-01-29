#!/bin/bash

#log output from this user_data script
exec > >(tee /var/log/user-data.log|logger -t user-data ) 2>&1

echo '${license}' > /home/dataiku/license.txt
chown dataiku:dataiku /home/dataiku/license.txt
chmod 600 /home/dataiku/license.txt

echo '${api_dynamic_settings_json}' > /opt/dataiku-configurator/dynamic-settings.json
chown dataiku:dataiku /opt/dataiku-configurator/dynamic-settings.json
chmod 600 /opt/dataiku-configurator/dynamic-settings.json

echo '${volume_dynamic_settings_json}' > /opt/volume-manager/dynamic-settings.json
chown dataiku:dataiku /opt/volume-manager/dynamic-settings.json
chmod 600 /opt/volume-manager/dynamic-settings.json
on