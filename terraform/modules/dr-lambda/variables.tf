variable "aws_region" {
  description = "The AWS region the bucket is to be created in"
  type        = string
}

variable "enable" {
  description = "Build the DR resources or not"
  type = bool
  default = true
}

variable "environment" {
  description = "Name of the environment we are deploying"
  type        = string
}

variable "lambda_deploy_option" {
  description = "Specify whether to build the lambda package as part of the terraform run, or pull a buildpack from S3. S3 or BUILD"
  type = string
  validation {
    condition     = length(regexall("^(S3|BUILD)$", var.lambda_deploy_option)) > 0
    error_message = "ERROR: Valid types are \"S3\" and \"BUILD\"!"
  }
  default = "BUILD"
}

variable "lambda_log_level" {
  description = "Set the logging level for lambda"
  type        = string
  default     = "INFO"
}

variable "cloudwatch_alarm_topic_name" {
  description = "Name of the SNS topic we will use for delivering cloudwatch alarms"
  type        = string
}

variable "source_s3_bucket_name" {
  description = "S3 bucket name to pull existing artefact from"
  type        = string
}

variable "source_s3_bucket_key" {
  description = "directory and artefact name within the bucket to pull"
  type        = string
  default     = "lambdas/backup-volume.zip"
}

variable "target_instance_tag" {
  description = "Provide a single tag for the lambda to target."
  type        = string
  default     = "DssRealtimeBackup"
}


locals {
  resource_title = "dss-${var.environment}"
}