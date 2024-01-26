module "snapshot-lifecycle" {
  source                = "../../../../modules/snapshot-lifecycle"
  enable_policy         = var.dlm_enable_policy
  resource_type         = "INSTANCE"
  retain_snapshot_count = var.dlm_retain_snapshot_count
  schedule_name         = var.dlm_schedule_name
  snapshot_time         = var.dlm_snapshot_time
  target_instance_tag   = var.dlm_target_instance_tag
}

module "dr_lambda" {
  source                      = "../../../../modules/dr-lambda"
  aws_region                  = var.aws_region
  cloudwatch_alarm_topic_name = var.dr_cloudwatch_alarm_sns_topic_name
  enable                      = var.dr_enable
  environment                 = var.environment
  lambda_deploy_option        = var.dr_lambda_deploy_option
  lambda_log_level            = var.dr_lambda_log_level
  source_s3_bucket_name       = var.dr_source_s3_bucket_name
  source_s3_bucket_key        = var.dr_source_s3_bucket_key
  target_instance_tag         = var.dr_target_instance_tag
}
