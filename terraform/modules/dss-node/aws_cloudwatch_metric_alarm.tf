resource "aws_cloudwatch_metric_alarm" "dataiku_dss_instance_failure" {
  alarm_name          = "${local.resource_title}-failed-instance"
  alarm_description   = "dataiku dss failed instance"
  comparison_operator = "GreaterThanThreshold"
  threshold           = "0"
  period              = "300"
  evaluation_periods  = "2"
  namespace           = "AWS/EC2"
  metric_name         = "StatusCheckFailed"
  statistic           = "Average"
  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.dataiku_dss.name
  }
  alarm_actions = [data.aws_sns_topic.topic.arn]
}

resource "aws_cloudwatch_metric_alarm" "dataiku_dss_excessive_cpu" {
  alarm_name          = "${local.resource_title}-excessive-cpu"
  alarm_description   = "CPU has been above the given threshold for an excessive amount of time"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "4"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "300"
  statistic           = "Average"
  threshold           = "90"
  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.dataiku_dss.name
  }
  alarm_actions = [data.aws_sns_topic.topic.arn]
}
