variable "additional_build_variables" {
  description = "A map of key-values that will be defined as environment variables in the codebuild project"
  type        = map(string)
  default     = {}
}

variable "ami_post_build_commands" {
  description = "Override the default ami post-build commands"
  type        = list(string)
  default     = []
}

variable "build_timeout" {
  description = "Time before build times out"
  type        = number
  default     = "60"
}

variable "compute_type" {
  description = "The builder instance class"
  type        = string
  default     = "BUILD_GENERAL1_SMALL"
}

variable "encrypt_ami" {
  type    = bool
  default = true
}

variable "environment_build_image" {
  description = "Docker image used by CodeBuild"
  type        = string
  default     = "aws/codebuild/standard:1.0"
}

variable "github_api_token" {
  description = "Personal Access Token used to connect CodeBuild projects to Github repositories"
  type        = string
}

variable "instance_type" {
  description = "Instance type used by packer to build"
  type        = string
  default     = "m5a.2xlarge"
}

variable "kms_key_arn" {
  description = "If Encrypt_ami set to true then you must pass in the arn of the key you wish to encrypt disk with."
  type        = string
  default     = ""
}

variable "packer_file_location" {
  description = "The file path of the .json packer to build."
  type        = string
}

variable "project_name" {
  type        = string
  description = "Name of the CodeBuild Project"
}

variable "region" {
  description = "The AWS region we are building in"
  type        = string
}

variable "root_volume_size" {
  description = "Specify the root volume size for the built image"
  type        = string
  default     = "150"
}

variable "s3_resource_arn" {
  description = "Name of a pre-existing module to allow access for build resources"
  type        = string
  default     = ""
}

variable "shared_ami_users" {
  description = "List of user accounts to share the built AMI with"
  type        = string
  default     = ""
}

variable "source_image_account_no" {
  description = "Account number owning the source image for the packer build"
  type        = string
  default     = "amazon"
}

variable "source_image_name" {
  description = "Name of an AMI to base the build on"
  type        = string
  default     = "amzn2-ami-hvm-*.*.*.*-*-gp2"
}

variable "source_repository_url" {
  type        = string
  description = "The source repository URL"
}

variable "subnet_name_filter" {
  description = "Tag value used to filter for private subnets we will be building in"
  type        = string
  default     = "Private*"
}

variable "vpc_name" {
  description = "Name of the VPC we are using"
  type        = string
}

locals {
  ami_install_commands = [
  ]

  ami_pre_build_commands = [
    "echo Installing HashiCorp Packer...",
    "curl -qL -o packer.zip https://releases.hashicorp.com/packer/1.10.0/packer_1.10.0_linux_amd64.zip && unzip -o packer.zip",
    "echo Create build number from git hash",
    "if [[ -z $BUILD_NUMBER ]]; then BUILD_NUMBER=$(git rev-parse --short HEAD); fi",
    "BUILD_INITIATOR=$CODEBUILD_INITIATOR",
    "echo Validating packer template to build...",
    "./packer validate ${var.packer_file_location}",
  ]

  ami_build_commands = [
    "./packer build -color=false ${var.packer_file_location} | tee build.log",
  ]

  ami_post_build_commands = length(var.ami_post_build_commands) != 0 ? var.ami_post_build_commands : [
    "egrep \"${var.region}\\:\\sami\\-\" build.log | cut -d' ' -f2 > ami_id.txt",
    "test -s ami_id.txt || exit 1",
    "if [ \"${var.encrypt_ami}\" = true ] ; then cp ami/templates/ami_builder_event.json . && sed -i.bak \"s/<<AMI-ID>>/$(cat ami_id.txt)/g\" ami_builder_event.json && aws events put-events --entries file://ami_builder_event.json; fi",
    "echo build completed on `date`",
  ]
}
