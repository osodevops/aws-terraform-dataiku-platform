data "aws_sns_topic" "topic" {
  name = var.cloudwatch_alarm_topic_name
}