# Function of the directory

The "containers" directory contains files used to construct customized "base containers" for dataiku.

## Points to note
- Images can be built manually from a development laptop via a packer command. See below for details
- Packer will use the latest built ami of dataiku to ensure any changes in dataikus code are included in the containers

## Directory structure
- `/containers/api-deployer`
- `/containers/container-exec`
- `/containers/spark`

These directories contain customization content for the three types of base container
See "Customizing the build" below for details of the files therein.

- `/containers/packer` Contains files related to or used by packer.

`build.json` is the packfile used by the CodeBuild project.

`environment.json` can be used to configure manual builds.

- `/containers/packer/scripts` Contains utility scripts used by Packer.

`build.sh` is the script that wraps the dataiku dssadmin utility.

`user_data.sh` is a small script used to prevent the dataiku service launching during the build process.

## The CodeBuild project
This is created by the dataiku Terraform

Note that when updating the customization content, you do not need to re-run Terraform since the CodeBuild project will pull the latest version of the repository and use that content.

To build and upload the base containers, start the `update-dataiku-containers` CodeBuild project

## Customizing the build
Each base container has a corresponding directory (e.g. container-exec) and each directory contains files that can be modified to customize the build

###`base_image.txt`
Contains the name of an optional docker source image.
e.g. `centos:7` or `09716644331.dkr.ecr.eu-west-2.amazonaws.com/myimage:latest`

To remove an image, save the file as empty

### `docker_fragments_append.txt`
Contains lines that will be appended to the Dockerfile. These can be any docker build commands that would normally be inside a Dockerfile

### `docker_fragments_prepend.txt`
Contains lines that will be appended to the Dockerfile. These can be any docker build commands that would normally be inside a Dockerfile

### **Note on docker fragment files**
The top and bottom lines of the docker fragment files should remain blank to avoid errors where the generated Dockerfile does not include a newline on at the point of insertion.

Commented reminders are in the given files

## Manually building containers

- Configure `/continers/packer/environment.json`. This file must contain values correct for the environment you intend to build in
- As an account with assume-role capability, execute the following:

`packer build -var-file containers/packer/environment.json containers/packer/build.json`