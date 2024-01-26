resource "aws_cloudwatch_metric_alarm" "snapshot_lambda_failure" {
  count = var.enable ? 1 : 0
  alarm_name          = "${local.resource_title}-Lambda-Failure"
  alarm_description   = "Dataiku backup settings failure (${var.environment})"
  comparison_operator = "GreaterThanThreshold"
  threshold           = "0"
  period              = "3600"
  evaluation_periods  = "1"
  namespace           = "Dataiku"
  metric_name         = "DataikuDSSUnexpectedLambdaFailure"
  statistic           = "SampleCount"
  treat_missing_data  = "notBreaching"
  dimensions = {
    Environment = var.environment,
  }
  alarm_actions = [data.aws_sns_topic.topic.arn]
}
