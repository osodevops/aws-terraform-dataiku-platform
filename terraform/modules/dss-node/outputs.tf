output "dataiku_dss_alb_dns" {
  value = aws_alb.dataiku_dss.dns_name
}

output "dataiku_dss_alb_zone" {
  value = aws_alb.dataiku_dss.zone_id
}

output "instance_security_group_id" {
  value = aws_security_group.dss.id
}
