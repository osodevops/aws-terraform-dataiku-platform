data "aws_route53_zone" "public" {
  count = var.r53_enable_public_zone && var.lb_enable_load_balancer ? 1 : 0
  name         = "${var.r53_zone_name}."
  private_zone = false
}

data "aws_route53_zone" "private" {
  count = var.r53_enable_private_zone && var.lb_enable_load_balancer ? 1 : 0
  name         = "${var.r53_zone_name}."
  private_zone = true
}
