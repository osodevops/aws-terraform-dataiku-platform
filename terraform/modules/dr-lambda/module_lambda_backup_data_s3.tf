module "backup_volume_s3" {
  count           = var.enable && var.lambda_deploy_option == "S3" ? 1 : 0
  create_function = true
  source          = "terraform-aws-modules/lambda/aws"
  version         = "~> 3.2"

  function_name  = "${local.resource_title}-backup-volume"
  description    = "Service to create snapshots on instance termination"
  handler        = "backup_volume.main.lambda_handler"
  create_package = false
  runtime        = "python3.8"
  timeout        = 90

  s3_existing_package = {
    bucket     = var.source_s3_bucket_name
    key        = var.source_s3_bucket_key
    version_id = null
  }

  environment_variables = tomap({
    REGION      = var.aws_region
    TAG_TARGET  = var.target_instance_tag
    LOG_LEVEL   = var.lambda_log_level
    MAX_WORKERS = 5
  })

  attach_policy = true
  policy        = one(aws_iam_policy.lambda_execution.*.arn)
  publish       = true

  allowed_triggers = {
    CloudwatchEvents = {
      principal  = "events.amazonaws.com",
      source_arn = one(aws_cloudwatch_event_rule.instance_termination.*.arn)
    }
  }
}

resource "aws_cloudwatch_event_target" "call_terminator_s3" {
  count           = var.enable && var.lambda_deploy_option == "S3" ? 1 : 0
  rule      = one(aws_cloudwatch_event_rule.instance_termination.*.name)
  target_id = "instanceTerminator"
  arn       = one(module.backup_volume_s3.*.lambda_function_arn)
}