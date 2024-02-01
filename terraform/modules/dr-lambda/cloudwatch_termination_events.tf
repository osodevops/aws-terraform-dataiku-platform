resource "aws_cloudwatch_event_rule" "instance_termination" {
  count = var.enable ? 1 : 0
  name          = "${local.resource_title}-instance-termination"
  description   = "Fires on instance terminated state event"
  event_pattern = jsonencode(
    {
      "source": [
        "aws.ec2"
      ],
      "detail-type": [
        "EC2 Instance State-change Notification"
      ],
      "account": [data.aws_caller_identity.current.account_id],
      "region": [var.aws_region],
      "detail": {
        "state": [
          "terminated"
        ]
      }
    })
}
