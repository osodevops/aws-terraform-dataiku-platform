data "aws_elb_service_account" "main" {}

#data "aws_iam_policy_document" "alb_access_logs" {
#  count = var.lb_enable_load_balancer ? 1 : 0
#  statement {
#    actions = [
#      "s3:PutObject",
#    ]
#
#    resources = [
#      "${one(module.lb_access_logs.*.s3_bucket_arn)}/*",
#    ]
#
#    principals {
#      identifiers = [data.aws_elb_service_account.main.arn]
#      type        = "AWS"
#    }
#  }
#}

resource "aws_alb_listener" "http" {
  count             = var.lb_enable_load_balancer ? 1 : 0
  load_balancer_arn = one(aws_alb.dataiku_dss.*.id)
  port              = var.lb_http_port
  protocol          = "HTTP"

  default_action {
    type = "redirect"
    redirect {
      port        = var.lb_https_port
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }

  depends_on = [aws_alb.dataiku_dss, aws_alb_target_group.tg]
}

resource "aws_alb_listener" "https" {
  count = var.lb_enable_load_balancer ? 1 : 0
  default_action {
    type             = "forward"
    target_group_arn = one(aws_alb_target_group.tg.*.id)
  }

  load_balancer_arn = one(aws_alb.dataiku_dss.*.id)
  port              = var.lb_https_port
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-Ext-2018-06"
  certificate_arn   = var.lb_certificate_arn

  depends_on = [aws_alb.dataiku_dss, aws_alb_target_group.tg]
}

resource "aws_alb_target_group" "tg" {
  count    = var.lb_enable_load_balancer ? 1 : 0
  // target group name limited to 32 characters and only alpha + num + hyphens
  name     = local.resource_title
  port     = var.dss_service_port
  protocol = var.dss_service_protocol
  vpc_id   = one(data.aws_vpc.dataiku_dss.*.id)

  health_check {
    interval            = 30
    path                = var.lb_health_check_path
    port                = var.lb_health_check_port
    protocol            = var.lb_health_check_protocol
    timeout             = var.lb_health_check_timeout
    healthy_threshold   = 2
    unhealthy_threshold = 2
    matcher             = var.lb_health_check_response_code
  }

  tags = {
    "Name" : local.resource_title
  }

  // based on https://github.com/hashicorp/terraform/issues/12634
  depends_on = [
    aws_alb.dataiku_dss
  ]
}

resource "aws_alb" "dataiku_dss" {
  count                      = var.lb_enable_load_balancer ? 1 : 0
  name                       = local.resource_title
  subnets                    = data.aws_subnets.public.ids
  internal                   = var.lb_internal
  enable_deletion_protection = var.lb_enable_deletion_protection
  security_groups            = [
    one(aws_security_group.lb.*.id)
  ]
  idle_timeout = 600

  access_logs {
    bucket  = one(module.lb_access_logs.*.s3_bucket_id)
    prefix  = var.lb_logs_s3_prefix
    enabled = var.lb_logs_s3_enabled
  }

  tags = {
    "Name" : local.resource_title,
    "DssNode" : title(var.dss_node_type)
  }

  depends_on = [
    module.lb_access_logs
  ]
}

resource "aws_autoscaling_attachment" "http_ui_port" {
  count                  = var.lb_enable_load_balancer ? 1 : 0
  autoscaling_group_name = one(aws_autoscaling_group.dataiku_dss.*.id)
  lb_target_group_arn    = one(aws_alb_target_group.tg.*.arn)
}

resource "aws_security_group" "lb" {
  count       = var.lb_enable_load_balancer ? 1 : 0
  description = "dataiku_dss UI - Managed by Terraform"
  name        = "${local.resource_title}-dss-lb"
  vpc_id      = data.aws_vpc.dataiku_dss.id
  tags        = {
    "Name" : "${local.resource_title}-dss-alb"
  }
}

resource "aws_vpc_security_group_ingress_rule" "http_in" {
  count             = length(var.lb_allowed_ips)
  security_group_id = one(aws_security_group.lb.*.id)
  description       = "Allow HTTP inbound from external CIDRs"
  from_port         = var.lb_http_port
  to_port           = var.lb_http_port
  ip_protocol       = "tcp"
  cidr_ipv4         = element(var.lb_allowed_ips, count.index)
}

resource "aws_vpc_security_group_ingress_rule" "https_in" {
  count             = length(var.lb_allowed_ips)
  security_group_id = one(aws_security_group.lb.*.id)
  description       = "Allow HTTPS inbound from external CIDR"
  from_port         = var.lb_https_port
  to_port           = var.lb_https_port
  ip_protocol       = "tcp"
  cidr_ipv4         = element(var.lb_allowed_ips, count.index)
}

resource "aws_vpc_security_group_ingress_rule" "additional_sg_access" {
  count                        = length(var.lb_allow_security_groups)
  security_group_id            = one(aws_security_group.lb.*.id)
  description                  = "Allow other nodes in on HTTPS, identified by a specific security group"
  from_port                    = var.lb_https_port
  to_port                      = var.lb_https_port
  ip_protocol                  = "tcp"
  referenced_security_group_id = data.aws_security_group.external_node_sg[count.index].id
}

resource "aws_vpc_security_group_egress_rule" "default_out" {
  security_group_id = one(aws_security_group.lb.*.id)
  description       = "Allow all outbound traffic"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}

module "lb_access_logs" {
  count         = var.lb_enable_load_balancer ? 1 : 0
  source        = "terraform-aws-modules/s3-bucket/aws"
  version       = "~> 4.1"
  bucket        = var.lb_log_s3_bucket_name

  acl    = "log-delivery-write"

  # Allow deletion of non-empty bucket
  force_destroy = true

  control_object_ownership = true
  object_ownership         = "ObjectWriter"

  attach_elb_log_delivery_policy = true

  tags = {
    "Name" : var.lb_log_s3_bucket_name
  }
}

resource "aws_cloudwatch_metric_alarm" "dataiku_dss_alb_unhealthy_hosts" {
  count               = var.lb_enable_load_balancer ? 1 : 0
  alarm_name          = "${local.resource_title}-dss-alb-unhealthy"
  alarm_description   = "dataiku dss ALB unhealthy hosts"
  comparison_operator = "GreaterThanThreshold"
  threshold           = "0"
  period              = "300"
  evaluation_periods  = "2"
  namespace           = "AWS/ApplicationELB"
  metric_name         = "UnHealthyHostCount"
  statistic           = "Average"
  dimensions          = {
    LoadBalancer = one(aws_alb.dataiku_dss.*.arn_suffix)
    TargetGroup  = one(aws_alb_target_group.tg.*.arn_suffix)
  }
  alarm_actions = [data.aws_sns_topic.topic.arn]
}
