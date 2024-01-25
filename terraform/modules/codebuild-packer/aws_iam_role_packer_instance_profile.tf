resource "aws_iam_role" "codebuild_instance_role" {
  name = "codebuild-packer-${var.project_name}"

  assume_role_policy = <<POLICY
{
  "Version": "2008-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": [
          "ec2.amazonaws.com",
          "ssm.amazonaws.com"
        ]
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
POLICY
}

resource "aws_iam_policy" "codebuild_instance_policy" {
  name        = "codebuild-packer-${var.project_name}"
  description = "Allow CodeBuild access to resources"
  policy      = data.aws_iam_policy_document.codebuild_instance_policy_document.json
}

resource "aws_iam_policy_attachment" "codebuild_instance_attach" {
  name       = "codebuild-packer-${var.project_name}"
  roles      = [aws_iam_role.codebuild_instance_role.name]
  policy_arn = aws_iam_policy.codebuild_instance_policy.arn
}

data "aws_iam_policy_document" "codebuild_instance_policy_document" {
  statement {
    sid    = "BasePermissions"
    effect = "Allow"
    actions = [
      "ssm:DescribeInstanceInformation",
      "ssm:DescribeAssociation",
      "ssm:GetDeployablePatchSnapshotForInstance",
      "ssm:GetDocument",
      "ssm:GetManifest",
      "ssm:GetParameters",
      "ssm:GetParameter",
      "ssm:ListAssociations",
      "ssm:ListInstanceAssociations",
      "ssm:PutInventory",
      "ssm:PutComplianceItems",
      "ssm:PutConfigurePackageResult",
      "ssm:UpdateAssociationStatus",
      "ssm:UpdateInstanceAssociationStatus",
      "ssm:UpdateInstanceInformation",
      "secretsmanager:GetSecretValue",
      "ssmmessages:CreateControlChannel",
      "ssmmessages:CreateDataChannel",
      "ssmmessages:OpenControlChannel",
      "ssmmessages:OpenDataChannel",
      "ec2messages:AcknowledgeMessage",
      "ec2messages:DeleteMessage",
      "ec2messages:FailMessage",
      "ec2messages:GetEndpoint",
      "ec2messages:GetMessages",
      "ec2messages:SendReply",
      "cloudwatch:PutMetricData",
      "ec2:DescribeInstanceStatus",
      "ec2:CreateTags",
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:DescribeLogGroups",
      "logs:DescribeLogStreams",
      "logs:PutLogEvents"
    ]
    resources = [
      "*"
    ]
  }

  statement {
    sid    = "EcrAccess"
    effect = "Allow"
    actions = [
      "ecr:GetRegistryPolicy",
      "ecr:DescribeRegistry",
      "ecr:GetAuthorizationToken",
      "ecr:DeleteRegistryPolicy",
      "ecr:PutRegistryPolicy",
      "ecr:PutReplicationConfiguration"
    ]
    resources = [
      "*"
    ]
  }

  statement {
    sid    = "EcrRepositorySpecific"
    effect = "Allow"
    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:BatchGetImage",
      "ecr:CreateRepository",
      "ecr:CompleteLayerUpload",
      "ecr:DescribeImages",
      "ecr:DescribeImageScanFindings",
      "ecr:DescribeRepositories",
      "ecr:GetDownloadUrlForLayer",
      "ecr:GetLifecyclePolicy",
      "ecr:GetLifecyclePolicyPreview",
      "ecr:GetRepositoryPolicy",
      "ecr:InitiateLayerUpload",
      "ecr:ListImages",
      "ecr:ListTagsForResource",
      "ecr:PutImage",
      "ecr:UploadLayerPart"
    ]
    resources = [
      "arn:aws:ecr:${var.region}:${data.aws_caller_identity.current.account_id}:repository/*"
    ]
  }
}

resource "aws_iam_policy" "codebuild_instance_s3_policy" {
  count       = var.s3_resource_arn != "" ? 1 : 0
  name        = "codebuild-packer-${var.project_name}-s3"
  description = "Allow CodeBuild access to S3resources"
  policy      = data.aws_iam_policy_document.codebuild_instance_s3_policy_document[count.index].json
}

resource "aws_iam_policy_attachment" "codebuild_instance_s3_attach" {
  count      = var.s3_resource_arn != "" ? 1 : 0
  name       = "codebuild-packer-${var.project_name}-s3"
  roles      = [aws_iam_role.codebuild_instance_role.name]
  policy_arn = aws_iam_policy.codebuild_instance_s3_policy[count.index].arn
}

data "aws_iam_policy_document" "codebuild_instance_s3_policy_document" {
  count = var.s3_resource_arn != "" ? 1 : 0
  statement {
    sid    = "1"
    effect = "Allow"
    actions = [
      "s3:PutObject",
      "s3:GetObject",
      "s3:AbortMultipartUpload",
      "s3:ListMultipartUploadParts",
      "s3:ListBucket",
      "s3:ListBucketMultipartUploads"
    ]
    resources = [
      var.s3_resource_arn,
      "${var.s3_resource_arn}/*"
    ]
  }
}

resource "aws_iam_instance_profile" "codebuild_ec2_iam_profile" {
  name = "codebuild-packer-${var.project_name}"
  role = aws_iam_role.codebuild_instance_role.name
}
