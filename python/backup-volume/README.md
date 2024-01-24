# Snapshot creation lambda
This code is intended to be run in an AWS lambda.

It performs the task of creating a snapshot of the current data volume for an instance when it is terminated.

The flow of operations is:
- A dataiku instance is terminated, which creates an AWS termination event
- The lambda receives the event
- If a data-volume is found that relates to the terminated instance, a snapshot of the volume is started
- A snapshot of the RDS database is also started

Note that the volume is not removed since the snapshotting process can take a few minutes - this is done by the dataiku instance if it starts up in the same availability zone as the volume. We do remove the "Snapshot" tag to prevent the scheduled snapshots created by the lifecycle rule from backing up the volume

## Environment variables
    REGION                  Name of the region we are operating in
    TAG_DATA_VOLUME         Value of the Data-volume tag to use
    TAG_APPLICATION         Value of the Application tag to use
    TAG_ENVIRONMENT         Value of the Environment tag to use
    MAX_WORKERS             Standard Lambda configuration. Typically 5

## Running the available tests
To excecute pytest against the code, execute the following
```shell
cd lambda/backup-volume
. test-env.sh
pipenv install -d
pipenv run pytest
```

## Building the lambda package
A zipfile should be created and stored in the repo. This is then picked up by Terraform and deployed as a lambda

To build a new zipfile, ensure you have version 3.8 of python available on the machine doing the build. Execute the following:
```shell
cd lambda/backup-volume
pipenv run ./build-function.sh -b
```
