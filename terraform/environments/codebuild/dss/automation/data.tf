# Uncomment to retrieve PAT from AWS Parameter Store
#data "aws_ssm_parameter" "github_pat" {
#  name = "/dss/${var.environment}/github_personal_access_token"
#}

# Uncomment to retrieve PAT from Hasihcorp Vault
#data "vault_generic_secret" "github_pat" {
#  path = var.vault_path_github_api_key
#}