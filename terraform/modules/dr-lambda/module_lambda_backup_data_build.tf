module "backup_volume_build" {
  count           = var.enable && var.lambda_deploy_option == "BUILD" ? 1 : 0
  create_function = true
  source          = "terraform-aws-modules/lambda/aws"
  version         = "~> 3.2"

  function_name  = "${local.resource_title}-backup-volume"
  description    = "Service to create snapshots on instance termination"
  handler        = "main.lambda_handler"
  create_package = true
  runtime        = "python3.8"
  timeout        = 90

  source_path = [
    "../../../../../python/backup-volume/src",
    {
      pip_requirements = "../../../../../python/backup-volume/requirements.txt"
    }
  ]

  environment_variables = tomap({
    REGION      = var.aws_region
    TAG_TARGET  = var.target_instance_tag
    LOG_LEVEL   = var.lambda_log_level
    MAX_WORKERS = 5
  })

  attach_policy = true
  policy        = aws_iam_policy.lambda_execution.arn
  publish       = true

  allowed_triggers = {
    CloudwatchEvents = {
      principal  = "events.amazonaws.com",
      source_arn = aws_cloudwatch_event_rule.instance_termination.arn
    }
  }
}


resource "aws_cloudwatch_event_target" "call_terminator" {
  count           = var.enable && var.lambda_deploy_option == "BUILD" ? 1 : 0
  rule      = aws_cloudwatch_event_rule.instance_termination.*.name
  target_id = "instanceTerminator"
  arn       = module.backup_volume_build.*.lambda_function_arn
}