variable "aws_region" {
  description = "AWS region we are managing"
  type        = string
}

variable "common_tags" {
  description = "A collection of common tags to be added to resources."
  type        = map(string)
}

variable "bucket_name_dss_config" {
  description = "Bucket name to create"
  type        = string
}

variable "bucket_name_ssm_logging" {
  description = "Bucket name to create"
  type        = string
}
