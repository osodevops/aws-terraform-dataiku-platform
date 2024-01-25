resource "aws_iam_role" "local_codebuild_role" {
  name               = "codebuild-${var.project_name}"
  description        = "Managed by Terraform"
  assume_role_policy = data.aws_iam_policy_document.forrole.json
}

data "aws_iam_policy_document" "forrole" {
  statement {
    effect = "Allow"

    principals {
      type = "Service"

      identifiers = [
        "codebuild.amazonaws.com",
      ]
    }

    actions = ["sts:AssumeRole"]
  }
}


resource "aws_iam_policy" "local_codebuild" {
  name        = "codebuild-${var.project_name}-policy"
  description = "Managed by Terraform: Policy used in trust relationship with CodeBuild"
  path        = "/service-role/"
  policy      = data.aws_iam_policy_document.local_codebuild.json
}

resource "aws_iam_role_policy_attachment" "local_codebuild" {
  role       = aws_iam_role.local_codebuild_role.name
  policy_arn = aws_iam_policy.local_codebuild.arn
}

data "aws_iam_policy_document" "local_codebuild" {
  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = [
      "*",
    ]

    effect = "Allow"
  }

  statement {
    actions = [
      "ssm:DescribeParameters",
      "ssm:PutParameter",
      "ssm:GetParameterHistory",
      "ssm:DescribeDocumentParameters",
      "ssm:GetParametersByPath",
      "ssm:GetParameters",
      "ssm:GetParameter",
    ]

    resources = [
      "*",
    ]

    effect = "Allow"
  }
  statement {
    sid    = "allowPackerPassRole"
    effect = "Allow"
    actions = [
      "iam:PassRole",
      "iam:GetInstanceProfile"
    ]
    resources = ["*"]
  }

  statement {
    sid       = "allowCodeBuildPushEvents"
    effect    = "Allow"
    actions   = ["events:PutEvents"]
    resources = ["*"]
  }

  statement {
    actions = [
      "ec2:AttachVolume",
      "ec2:AuthorizeSecurityGroupIngress",
      "ec2:CopyImage",
      "ec2:CreateImage",
      "ec2:CreateKeypair",
      "ec2:CreateNetworkInterface",
      "ec2:CreateSecurityGroup",
      "ec2:CreateSnapshot",
      "ec2:CreateTags",
      "ec2:CreateVolume",
      "ec2:DeleteKeypair",
      "ec2:DeleteNetworkInterface",
      "ec2:DeleteSecurityGroup",
      "ec2:DeleteSnapshot",
      "ec2:DeleteVolume",
      "ec2:DeregisterImage",
      "ec2:DescribeImageAttribute",
      "ec2:DescribeImages",
      "ec2:DescribeInstances",
      "ec2:DescribeDhcpOptions",
      "ec2:DescribeNetworkInterfaces",
      "ec2:DescribeRegions",
      "ec2:DescribeSecurityGroups",
      "ec2:DescribeSnapshots",
      "ec2:DescribeSubnets",
      "ec2:DescribeVpcs",
      "ec2:CreateNetworkInterfacePermission",
      "ec2:DescribeTags",
      "ec2:DescribeVolumes",
      "ec2:DetachVolume",
      "ec2:GetPasswordData",
      "ec2:ModifyImageAttribute",
      "ec2:ModifyInstanceAttribute",
      "ec2:ModifySnapshotAttribute",
      "ec2:RegisterImage",
      "ec2:RunInstances",
      "ec2:StopInstances",
      "ec2:TerminateInstances",
    ]

    resources = [
      "*",
    ]

    effect = "Allow"
  }
}
