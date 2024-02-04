resource "aws_iam_role" "dss" {
  name               = local.resource_title
  description        = "Allows EC2 instances to call AWS services like CloudWatch and SSM on your behalf."
  assume_role_policy = data.aws_iam_policy_document.dss_assume_role.json
}

resource "aws_iam_instance_profile" "dss" {
  name = local.resource_title
  role = aws_iam_role.dss.name
}

data "aws_iam_policy_document" "dss_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type = "Service"

      identifiers = [
        "s3.amazonaws.com",
        "ec2.amazonaws.com",
        "ssm.amazonaws.com"
      ]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_policy" "dss_instance_s3" {
  count       = var.s3_allow_instance_bucket ? 1 : 0
  name        = "${local.resource_title}-instance-s3"
  description = "Policy for DSS instance S3 interactions"
  policy      = data.aws_iam_policy_document.dss_instance_s3.*.json
}

resource "aws_iam_role_policy_attachment" "dss_instance_s3" {
  count      = var.s3_allow_instance_bucket ? 1 : 0
  role       = aws_iam_role.dss.name
  policy_arn = aws_iam_policy.dss_instance_s3.*.arn
}

data "aws_iam_policy_document" "dss_instance_s3" {
  count = var.s3_allow_instance_bucket ? 1 : 0
  statement {
    sid    = "S3BucketAccess"
    effect = "Allow"

    actions = [
      "s3:ListBucket",
      "s3:HeadBucket",
      "s3:PutObject",
      "s3:PutObjectTagging",
      "s3:DeleteObject",
      "s3:DeleteObjectVersion",
      "s3:ListObjects",
      "s3:GetObject",
      "s3:GetObjectTagging",
      "s3:GetBucketLocation",
      "s3:GetEncryptionConfiguration",
      "s3:AbortMultipartUpload",
      "s3:ListMultipartUploadParts",
      "s3:ListBucketMultipartUploads"
    ]

    resources = [
      "arn:aws:s3:::${var.s3_instance_bucket_name}",
      "arn:aws:s3:::${var.s3_instance_bucket_name}/*"
    ]
  }
}

resource "aws_iam_policy" "dss_config_s3" {
  count       = var.dss_s3_config_bucket !="" ? 1 : 0
  name        = "${local.resource_title}-config-s3"
  description = "Policy for DSS instance S3 interactions for config"
  policy      = one(data.aws_iam_policy_document.dss_config_s3.*.json)
}

resource "aws_iam_role_policy_attachment" "dss_config_s3" {
  count       = var.dss_s3_config_bucket !="" ? 1 : 0
  role       = aws_iam_role.dss.name
  policy_arn = one(aws_iam_policy.dss_config_s3.*.arn)
}

data "aws_iam_policy_document" "dss_config_s3" {
  count       = var.dss_s3_config_bucket !="" ? 1 : 0
  statement {
    sid    = "S3BucketConfigAccess"
    effect = "Allow"

    actions = [
      "s3:ListBucket",
      "s3:HeadBucket",
      "s3:ListObjects",
      "s3:GetObject",
      "s3:GetObjectTagging",
      "s3:GetBucketLocation",
      "s3:GetEncryptionConfiguration",
    ]

    resources = [
      "arn:aws:s3:::${var.dss_s3_config_bucket}",
      "arn:aws:s3:::${var.dss_s3_config_bucket}/*"
    ]
  }
}

resource "aws_iam_policy" "dss_instance_session" {
  count       = var.s3_session_logging_bucket_arn != "" ? 1 : 0
  name        = "${local.resource_title}-instance-session-logs"
  description = "Policy for DSS instance Session logging"
  policy      = one(data.aws_iam_policy_document.dss_instance_session.*.json)
}

resource "aws_iam_role_policy_attachment" "dss_instance_session" {
  count      = var.s3_session_logging_bucket_arn != "" ? 1 : 0
  role       = aws_iam_role.dss.name
  policy_arn = one(aws_iam_policy.dss_instance_session.*.arn)
}

data "aws_iam_policy_document" "dss_instance_session" {
  count = var.s3_session_logging_bucket_arn != "" ? 1 : 0
  statement {
    sid     = "S3SessionLogging"
    effect  = "Allow"
    actions = [
      "s3:PutObject"
    ]
    resources = ["${var.s3_session_logging_bucket_arn}/*"]
  }

  statement {
    sid     = "encryptionConfig"
    effect  = "Allow"
    actions = [
      "s3:GetEncryptionConfiguration"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "dss_instance_general" {
  name        = "${local.resource_title}-instance-general"
  description = "Policy for DSS instance general interactions"
  policy      = data.aws_iam_policy_document.dss_instance_general.json
}

resource "aws_iam_role_policy_attachment" "dss_instance_general" {
  role       = aws_iam_role.dss.name
  policy_arn = aws_iam_policy.dss_instance_general.arn
}

data "aws_iam_policy_document" "dss_instance_general" {
  statement {
    sid     = "generateDataKey"
    effect  = "Allow"
    actions = [
      "kms:GenerateDataKey"
    ]
    resources = ["*"]
  }

  statement {
    sid    = "SsmSpecificParameters"
    effect = "Allow"

    actions = [
      "ssm:GetParameterHistory",
      "ssm:GetParametersByPath",
      "ssm:GetParameters",
      "ssm:GetParameter",
      "ssm:PutParameter"
    ]

    resources = [
      "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/*",
    ]
  }

  statement {
    sid    = "SsmAllResources"
    effect = "Allow"

    actions = [
      "ssm:DescribeParameters",
      "ssm:DescribeAssociation",
      "ssm:GetDeployablePatchSnapshotForInstance",
      "ssm:GetDocument",
      "ssm:DescribeDocument",
      "ssm:GetManifest",
      "ssm:ListAssociations",
      "ssm:ListInstanceAssociations",
      "ssm:PutInventory",
      "ssm:PutComplianceItems",
      "ssm:PutConfigurePackageResult",
      "ssm:UpdateAssociationStatus",
      "ssm:UpdateInstanceAssociationStatus",
      "ssm:UpdateInstanceInformation",
      "ssmmessages:CreateControlChannel",
      "ssmmessages:CreateDataChannel",
      "ssmmessages:OpenControlChannel",
      "ssmmessages:OpenDataChannel",
      "ec2messages:AcknowledgeMessage",
      "ec2messages:DeleteMessage",
      "ec2messages:FailMessage",
      "ec2messages:GetEndpoint",
      "ec2messages:GetMessages",
      "ec2messages:SendReply"
    ]

    resources = [
      "*",
    ]
  }

  statement {
    sid     = "Ec2Attachments"
    actions = [
      "ec2:AttachVolume",
      "ec2:DescribeInstances",
      "ec2:DescribeVolumes",
      "ec2:DescribeTags",
      "ec2:DescribeNetworkInterfaces",
      "ec2:DescribeInstanceStatus",
      "ec2:CreateVolume",
      "ec2:DeleteVolume",
      "ec2:CreateTags",
      "ec2:DeleteTags",
      "ec2:DescribeSnapshots",
      "ec2:DescribeSnapshotAttribute",
      "autoscaling:DescribeAutoScalingGroups",
      "kms:CreateGrant",
    ]

    resources = ["*"]
    effect    = "Allow"
  }

  statement {
    sid     = "DirectoryService"
    actions = [
      "ds:CreateComputer",
      "ds:DescribeDirectories"
    ]

    resources = ["*"]
    effect    = "Allow"
  }

  statement {
    sid     = "CloudwatchLogging"
    actions = [
      "cloudwatch:PutMetricData",
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:DescribeLogGroups",
      "logs:DescribeLogStreams",
      "logs:PutLogEvents"
    ]

    resources = ["*"]
    effect    = "Allow"
  }

  statement {
    sid     = "EcrAccess"
    effect  = "Allow"
    actions = [
      "ecr:GetRegistryPolicy",
      "ecr:DescribeRegistry",
      "ecr:GetAuthorizationToken",
      "ecr:DeleteRegistryPolicy",
      "ecr:PutRegistryPolicy",
      "ecr:PutReplicationConfiguration"
    ]
    resources = [
      "*",
    ]
  }

  statement {
    sid     = "ElasticLoadBalancer"
    effect  = "Allow"
    actions = [
      "elasticloadbalancing:DescribeLoadBalancers"
    ]

    resources = [
      "*",
    ]
  }

  statement {
    sid     = "EcrRepositorySpecific"
    effect  = "Allow"
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
      "arn:aws:ecr:${var.aws_region}:${data.aws_caller_identity.current.id}:repository/*",
    ]
  }
}
