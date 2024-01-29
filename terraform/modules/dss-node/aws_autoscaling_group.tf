resource "aws_launch_template" "dataiku_dss_launch_template" {
  name_prefix   = local.resource_title
  image_id      = data.aws_ami.dataiku_dss.id
  instance_type = var.instance_type
  key_name      = var.ssh_key_name
  network_interfaces {
    associate_public_ip_address = false

    security_groups = [
      aws_security_group.dss.id,
      aws_security_group.ssh.id
    ]
  }

  user_data = base64encode(templatefile("${path.module}/templates/cloud_init_dataiku_dss.sh", {
    region                       = var.aws_region
    environment                  = var.environment
    api_dynamic_settings_json    = jsonencode(local.api_dynamic_settings_json)
    volume_dynamic_settings_json = jsonencode(var.volume_dynamic_settings_json)
  }))

  iam_instance_profile {
    arn = aws_iam_instance_profile.dss.arn
  }

  block_device_mappings {
    device_name = "/dev/xvda"
    ebs {
      volume_size = var.root_volume_size
      volume_type = "gp3"
      encrypted   = var.encrypt_ebs
    }
  }

  monitoring {
    enabled = true
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_autoscaling_group" "dataiku_dss" {
  name                = local.resource_title
  vpc_zone_identifier = data.aws_subnets.private.ids
  min_size            = var.asg_min_size
  max_size            = var.asg_max_size
  desired_capacity    = var.asg_desired_capacity

  launch_template {
    name    = aws_launch_template.dataiku_dss_launch_template.name
    version = aws_launch_template.dataiku_dss_launch_template.latest_version
  }
  lifecycle {
    create_before_destroy = false
    ignore_changes        = [load_balancers, target_group_arns]
  }

  depends_on = [aws_security_group.dss]

  dynamic "tag" {
    for_each = local.asg_tags
    content {
      key                 = tag.value.key
      value               = tag.value.value
      propagate_at_launch = true
    }
  }
}
