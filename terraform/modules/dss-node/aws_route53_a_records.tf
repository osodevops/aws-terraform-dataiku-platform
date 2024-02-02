resource "aws_route53_record" "public" {
  count = var.r53_enable_public_zone && var.lb_enable_load_balancer ? 1 : 0

  zone_id = one(data.aws_route53_zone.public[*].zone_id)
  name    = local.resource_title
  type    = "A"

  alias {
    evaluate_target_health = false
    name                   = one(aws_alb.dataiku_dss.*.dns_name)
    zone_id                = one(aws_alb.dataiku_dss.*.zone_id)
  }
}
resource "aws_route53_record" "private" {
  count = var.r53_enable_private_zone && var.lb_enable_load_balancer ? 1 : 0

  zone_id = one(data.aws_route53_zone.private[*].zone_id)
  name    = local.resource_title
  type    = "A"

  alias {
    evaluate_target_health = false
    name                   = one(aws_alb.dataiku_dss.*.dns_name)
    zone_id                = one(aws_alb.dataiku_dss.*.zone_id)
  }
}
