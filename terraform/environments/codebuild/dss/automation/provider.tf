provider "aws" {
  region = var.aws_region
  default_tags {
    tags = var.common_tags
  }
}

#provider "vault" {
#  address = var.vault_address
#  auth_login {
#    path   = "auth/${var.vault_env}/login"
#    method = "aws"
#    parameters = {
#      role = var.vault_role
#    }
#  }
#  skip_tls_verify = true
#}
