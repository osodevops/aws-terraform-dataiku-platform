module "codebuild_automation" {
  source                     = "../../../../modules/codebuild-packer"
  # source                     = "osodevops/dataiku-dss/codebuild-packer#123456"
  additional_build_variables = { "NODE_TYPE": "automation" }
  encrypt_ami                = var.encrypt_ami
  kms_key_arn                = var.kms_key_arn
  instance_type              = var.packer_instance_type
  packer_file_location       = var.packer_file_location
  project_name               = var.project_name
  region                     = var.aws_region
  root_volume_size           = var.root_volume_size
  shared_ami_users           = var.shared_ami_users
  source_image_account_no    = var.source_image_account_no
  source_image_name          = var.source_image_name
  source_repository_url      = var.source_repository_url
  subnet_name_filter         = var.build_subnet_name_filter
  vpc_name                   = var.vpc_name
  # github_api_token           = data.aws_ssm_parameter.github_pat  # Uncomment to provide PAT from Parameter Store
  # github_api_token           = data.vault_generic_secret.github_pat  # Uncomment to provide PAT from Vault
}
