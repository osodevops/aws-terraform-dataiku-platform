# Volume manager
This code is currently provisioned by ansible and deployed with a systemd service file

It performs the task of creating a data volume from a pre-existing snapshot, formatting it, and mounting it into the operating system

This service is configured via a "dynamic-settings.json" file which should be deployed alongside the code, typically via Terraform.

## Environment variables
    LOG_LEVEL               Level of logging e.g. "INFO", "DEBUG"
    MAX_WORKERS             Standard Lambda configuration. Typically 5
    REGION                  Name of the region we are operating in
    TAG_DATA_VOLUME         Value of the "Data-volume" tag. Used to determine which DSS node this is the data volume for. e.g. "design"
    TAG_APPLICATION         Value of the "Application" tag. Typically "Dataiku-DSS"
    TAG_ENVIRTONMENT        Value of the "Deployment" tag. Used to differentiate between deployments in the same account
    ENCRYPT_VOLUMES         Whether to encrypt the new data volume
    VOLUME_IOPS             Some disk types (e.g. gp3) allow specifying IOPS. For "gp3" leave blank
    VOLUME_SIZE             Size in GB of the created data volume
    VOLUME_DEVICE_NAME      OS device where the disk should appear. e.g. /dev/xvdb
    VOLUME_MOUNT_POINT      Where the data volume will be mounted on the OS

# Building a pip
First execute all available tests
```bash
cd instance_termination
pipenv install -d
. test-env.sh
pipenv run pytest
```

Build the pip and wheel artefacts
```shell
pipenv run python -m build
```