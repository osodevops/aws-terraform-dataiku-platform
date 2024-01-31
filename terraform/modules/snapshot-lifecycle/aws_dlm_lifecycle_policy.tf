resource "aws_iam_role" "dlm_lifecycle_role" {
  name = "dlm-${var.schedule_name}"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "dlm.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "dlm_lifecycle" {
  name = "dlm-${var.schedule_name}"
  role = aws_iam_role.dlm_lifecycle_role.id

  policy = <<EOF
{
   "Version": "2012-10-17",
   "Statement": [
      {
         "Effect": "Allow",
         "Action": [
            "ec2:CreateSnapshot",
            "ec2:CreateSnapshots",
            "ec2:DeleteSnapshot",
            "ec2:DescribeInstances",
            "ec2:DescribeVolumes",
            "ec2:DescribeSnapshots"
         ],
         "Resource": "*"
      },
      {
         "Effect": "Allow",
         "Action": [
            "ec2:CreateTags"
         ],
         "Resource": "arn:aws:ec2:*::snapshot/*"
      }
   ]
}
EOF
}

resource "aws_dlm_lifecycle_policy" "dlm_policy" {
  description        = "DLM lifecycle policy"
  execution_role_arn = aws_iam_role.dlm_lifecycle_role.arn
  state              = var.enable_policy ? "ENABLED" : "DISABLED"

  policy_details {
    resource_types = [var.resource_type]

    schedule {
      name = var.schedule_name

      create_rule {
        interval      = var.snapshot_interval
        interval_unit = "HOURS"
        times         = [var.snapshot_time]
      }

      retain_rule {
        count = var.retain_snapshot_count
      }
      copy_tags = var.copy_tags
    }

    parameters {
      exclude_boot_volume = true
    }
    target_tags = {
      "${var.target_instance_tag}" = "True"
    }
  }
}