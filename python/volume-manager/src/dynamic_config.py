import json


class DynamicConfig:
    config: dict
    defaults: dict

    def __init__(self, filename):
        # Set some common defaults
        self.defaults = {
            "region": "eu-west-2",
            "encrypt_volumes": False,
            "volume_iops": "",
            "kms_key": "",
            "volume_type": "gp3",
            "volume_size": 40,
            "volume_device_name": "/dev/xvdb",
            "volume_mount_point": "/data"
        }
        try:
            with open(filename, 'r') as f:
                file_values = json.loads(f.read())
        except FileNotFoundError:
            print("configuration file has not been deployed. Ending run")
            sys.exit()
        except (OSError, json.JSONDecodeError) as err:
            print("Could not open/read the dynamic configuration file:", err)
            raise

        self.config = {**self.defaults, **file_values}

    def get(self, key):
        value = self.config.get(key, None)
        if value is None:
            raise Exception("Error getting dynamic config item \"%s\"", key)

        return value
