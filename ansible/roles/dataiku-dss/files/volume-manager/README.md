# Volume manager
This code is currently provisioned by ansible and deployed with a systemd service file

It performs the task of creating a data volume from a pre-existing snapshot, formatting it, and mounting it into the operating system

This service is configured via a "dynamic-settings.json" file which should be deployed alongside the code, typically via Terraform.

## Running pre-requisites
The code is assumed to run on a Dataiku DSS node requiring a data volume.

## Environment variables
    LOG_LEVEL               Level of logging e.g. "INFO", "DEBUG"

## Dynamic-settings.json
This file should contain run-time settings that allow the code to do its job. These are:
```json
{
  "region": "The AWS region we are using",
  "volume_type": "EBS storage type. e.g. gp3, io1",
  "volume_iops": "Where storage types support an explicit iops value, this can be provided",
  "volume_size": "In GB",
  "mount_point": "Where on the filesystem to mount the data volume. Typically /data",
  "encrypt_volumes": "Whether to create new volumes as encrypted or not",
  "kms_key": "If encrypted, an optional custom kms key can be provided. Otherwise the AWS default EBS key will be used",
  "device_name": "The system block-storage device. Typically /dev/xvdb. Should not need to change"
}
```

## Runtime instance tags
The codebase also relies on some tags that are common to all DSS nodes deployed via the codebase
- Name - Which must be distinct from any other running node
- Environment - e.g. pre-prod, staging, production

## Behaviour
- If a snapshot with the correct tags exists
  - Delete any pre-existing volume
  - Create a new volume from the snapshot (the snapshot is the saource of truth)
- If no snapshot exists
  - Create a new volume based on the default DSS installation from the AMI

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