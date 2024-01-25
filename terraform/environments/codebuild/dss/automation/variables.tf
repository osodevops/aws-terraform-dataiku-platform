variable "aws_region" {
  description = "The AWS region in which all resources will be created"
  type        = string
}

variable "build_subnet_name_filter" {
  description = "Used to filter by 'Name' tag for the subnets we will be building in"
  type        = string
  default     = "Private*"
}

variable "common_tags" {
  description = "A collection of common tags to be added to resources."
  type        = map(string)
}

variable "encrypt_ami" {
  description = "Encrypt AMI after successful build."
  type        = string
  default     = false
}

variable "kms_key_arn" {
  description = "If Encrypt_ami set to true then you must pass in the arn of the key you wish to encrypt disk with."
  type        = string
  default     = ""
}

variable "packer_file_location" {
  description = "The file path of the .json packer to build."
  type        = string
  default     = "packer/dataiku-dss.json"
}

variable "packer_instance_type" {
  description = "Instance type used by packer to build"
  type        = string
  default     = "m5a.2xlarge"
}

variable "project_name" {
  description = "Name of the CodeBuild Project"
  type        = string
}

variable "root_volume_size" {
  description = "Specify the root volume size for the built image"
  type        = string
  default     = "150"
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
  description = "The source repository for the packer and ansible build code"
  type        = string
}

variable "vpc_name" {
  description = "Name of the VPC we will be building in"
  type        = string
}

variable "vault_env" {
  description = "the vault environment variable."
  type        = string
}

variable "vault_role" {
  description = "the vault role to enable permissions to access the vault installation."
  type        = string
}

variable "vault_address" {
  description = "the vault host address pointing to the vault installation."
  type        = string
}

variable "vault_path_github_api_key" {
  description = "Vault path of the github api key secret"
  type        = string
  default     = ""
}

variable "vault_skip_tls" {
  description = "Whether to skip TLS verification for simple Vault installations"
  type        = bool
  default     = true
}
