module "access_sg" {
  source      = "../../../../modules/roles-and-security"
  count       = length(var.security_group_target_names)
  target_name = var.security_group_target_names[count.index]
  vpc_name    = var.vpc_name
}
