variable "aws_region" {
  description = "The AWS region in which all resources will be created"
  type        = string
}

variable "build_subnet_name_filter" {
  description = "Used to filter by 'Class' tag for the subnets we will be building in"
  type        = string
  default     = "Private*"
}

variable "build_timeout" {
  description = "Maximum running time for the job"
  type        = number
  default     = 180
}

variable "common_tags" {
  description = "A collection of common tags to be added to resources."
  type        = map(string)
}

variable "container_packer_instance_type" {
  description = "Instance type used by packer to build"
  type        = string
  default     = "m5a.2xlarge"
}

variable "container_source_image_account_no" {
  description = "Account number owning the source image for the packer build"
  type        = string
  default     = "amazon"
}

variable "container_source_repository_url" {
  description = "The source repository URL of OSO DevOps Tableau module."
  type        = string
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

variable "source_image_account_no" {
  description = "Account number owning the source image for the packer build"
  type        = string
  default     = "amazon"
}

variable "source_repository_url" {
  description = "The source repository URL of OSO DevOps Tableau module."
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

locals {
  container_additional_build_variables = { "ECR_ADDRESS" : "${local.ecr_registry_id_container_exec}/${var.deployment != "" ? var.deployment : var.environment}" }
  registry_prefix                      = var.deployment != "" ? var.deployment : var.environment

  ecr_registry_id_container_exec = trimsuffix(data.aws_ecr_repository.dataiku_common_container_exec.repository_url, "/${data.aws_ecr_repository.dataiku_common_container_exec.name}")
}