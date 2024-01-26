aws_region  = "MY-AWS-REGION"
common_tags = {
  Application = "Dataiku-DSS"
  Tool        = "Terraform"
}

# This wrapper can be deployed for a whole VPC, or for sub-sections of your environment. Tailor to suit.
environment = "common"

###################################################
# Options for Data Lifecycle Management rules (passive, scheduled backups)
###################################################

# Enable the DLM policy
dlm_enable_policy = true

# How many historical snapshots to keep
dlm_retain_snapshot_count = 7

# Name for the policy
dlm_schedule_name = "1 week of daily snapshots"

# Time in 24 hour notation for the snapshot policy to be evaluated
dlm_snapshot_time = "23:00"

# Regular backups via DLM will target instances with any of these tags and values
dlm_target_instance_tag = {
  DssSnapshot = "True"
}

###################################################
# Options for real-time snapshot solution
###################################################

# Name of a pre-existing SNS topic for lambda failure alarms
dr_cloudwatch_alarm_sns_topic_name = "MY-CLOUDWATCH-SNS-TOPIC"

# Whether to build the real-time lambda resources
dr_enable = true

# Build the lambda locally (BUILD) or pull a pre-existing package from S3 (S3)
dr_lambda_deploy_option = "BUILD"

# Logging level for the lambda captured in Cloudwatch
dr_lambda_log_level = "INFO"

# Bucket and key for the S3 lambda option. Ignored in the case of BUILD
dr_source_s3_bucket_name = "NAME-OF-AN-S3-BUCKET"
dr_source_s3_bucket_key = "KEY-OF-BUILT-LAMBDA-SOURCE"

# Any volume containing this tag will be selected for instant snapshot when an instance is terminated. Value on the instance must be "true"
dr_target_instance_tag = "DssRealtimeBackup"
