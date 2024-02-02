resource "aws_security_group" "dss" {
  vpc_id      = data.aws_vpc.dataiku_dss.id
  name        = "${local.resource_title}-instance"
  description = "dataiku dss - Managed by Terraform"

  tags = {
    "Name" : "${local.resource_title}-instance"
  }
}

resource "aws_vpc_security_group_ingress_rule" "ingress_alb" {
  count                        = var.lb_enable_load_balancer ? 1 : 0
  security_group_id            = one(aws_security_group.dss.*.id)
  description                  = "Allow service port traffic inbound from the ALB"
  from_port                    = var.dss_service_port
  to_port                      = var.dss_service_port
  ip_protocol                  = "tcp"
  referenced_security_group_id = one(aws_security_group.lb.*.id)
}

resource "aws_vpc_security_group_ingress_rule" "ingress_target_port" {
  count             = length(var.instance_allowed_ips) > 0 ? 1 : 0
  security_group_id = one(aws_security_group.dss.*.id)
  description       = "Allow service port traffic inbound from allowed IPs"
  from_port         = var.dss_service_port
  to_port           = var.dss_service_port
  ip_protocol       = "tcp"
  cidr_ipv4         = flatten(var.instance_allowed_ips)
}

resource "aws_vpc_security_group_egress_rule" "egress" {
  security_group_id = one(aws_security_group.dss.*.id)
  description       = "Allow all outbound traffic"
  cidr_ipv4       = "0.0.0.0/0"
  ip_protocol       = "-1"
}

resource "aws_security_group" "ssh" {
  name        = "${local.resource_title}-ssh"
  description = "Managed by Terraform"
  vpc_id      = data.aws_vpc.dataiku_dss.id
  tags        = {
    "Name" : "${local.resource_title}-ssh"
  }
}

resource "aws_vpc_security_group_ingress_rule" "ingress_target_port_ssh" {
  count             = length(var.instance_allowed_ips) > 0 ? 1 : 0
  security_group_id = aws_security_group.ssh.id
  description       = "Allow port 22 access from allowed internal ips"
  from_port         = 22
  to_port           = 22
  ip_protocol       = "tcp"
  cidr_ipv4         = flatten(var.instance_allowed_ips)
}

resource "aws_vpc_security_group_egress_rule" "egress_ssh" {
  security_group_id = one(aws_security_group.ssh.*.id)
  description       = "Allow all outbound traffic"
  cidr_ipv4       = "0.0.0.0/0"
  ip_protocol       = "-1"
}
