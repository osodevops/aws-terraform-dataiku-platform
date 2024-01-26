data "aws_iam_policy_document" "lambda_execution" {
  count = var.enable ? 1 : 0
  statement {
    sid = "ec2Policies"
    actions = [
      "ec2:DescribeInstances",
      "ec2:DescribeTags",
      "ec2:DeleteVolume",
      "ec2:DescribeVolumes",
      "ec2:DescribeSnapshots",
      "ec2:CreateSnapshot",
      "ec2:CreateTags",
      "ec2:DeleteTags",
      "cloudwatch:PutMetricData"
    ]
    resources = [
      "*",
    ]
  }

  statement {
    sid = "RdsPolicies"
    actions = [
      "rds:CreateDBSnapshot",
      "rds:AddTagsToResource"
    ]
    resources = [
      "*",
    ]
  }
}

resource "aws_iam_policy" "lambda_execution" {
  count = var.enable ? 1 : 0
  name        = "${local.resource_title}-lambda-execution"
  description = "Allow access to resources for lambda"
  policy      = data.aws_iam_policy_document.lambda_execution.*.json
}
