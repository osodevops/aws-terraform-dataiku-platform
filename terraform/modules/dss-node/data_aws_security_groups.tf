data "aws_security_group" "external_node_sg" {
  count = length(var.lb_allow_security_groups)
  name = element(var.lb_allow_security_groups, count.index)
}