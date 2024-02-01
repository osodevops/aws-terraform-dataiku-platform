variable "aws_region" {
  description = "AWS region we are managing"
  type        = string
}

variable "common_tags" {
  description = "A collection of common tags to be added to resources."
  type        = map(string)
}

variable "dlm_schedule_name" {
  description = "The name of the lifecycle schedule."
  type        = string
}

variable "dlm_enable_policy" {
  description = "policy state can be ENABLED DISABLED."
  type        = bool
  default     = true
}

variable "dlm_target_instance_tag" {
  description = "Provide a map of tags for the DLM to target."
  type        = string
  default     = "DLMSnapshot"
}

variable "dr_cloudwatch_alarm_sns_topic_name" {
  description = "Name of a pre-existing SNS topic for cloudwatch alarms"
  type        = string
}

variable "dr_target_instance_tag" {
  description = "Provide a single tag for the lambda to target."
  type        = string
  default     = "DRSnapshot"
}

variable "dlm_retain_snapshot_count" {
  description = "The number of snapshots for DLM to retain"
  type        = number
  default     = 7
}

variable "dlm_snapshot_time" {
  description = "When should the snapshot policy be evaluated"
  type        = string
  default     = "23:45"
}

variable "dr_enable" {
  description = "Whether to build the real-time DR solution"
  type        = bool
  default     = true
}

variable "dr_lambda_deploy_option" {
  description = "Specify whether to build the lambda package as part of the terraform run, or pull a buildpack from S3. S3 or BUILD"
  type        = string
  validation {
    condition     = length(regexall("^(S3|BUILD)$", var.dr_lambda_deploy_option)) > 0
    error_message = "ERROR: Valid types are \"S3\" and \"BUILD\"!"
  }
  default = "BUILD"
}

variable "dr_lambda_log_level" {
  description = "Set the logging level for lambda"
  type        = string
  default     = "INFO"
}

variable "dr_snapshot_time" {
  description = "When should the rule be evaluated"
  type        = string
  default     = "23:45"
}

variable "dr_source_s3_bucket_name" {
  description = "S3 bucket name to pull existing artefact from"
  type        = string
  default     = ""
}

variable "dr_source_s3_bucket_key" {
  description = "directory and artefact name within the bucket to pull"
  type        = string
  default     = "lambdas/backup-volume.zip"
}

variable "environment" {
  description = "Name of the environment we are deploying"
  type        = string
}