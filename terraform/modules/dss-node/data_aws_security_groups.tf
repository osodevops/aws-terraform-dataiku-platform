data "aws_security_group" "external_node_sg" {
  count = length(var.lb_additional_security_groups)
  name = element(var.lb_additional_security_groups, count.index)
}