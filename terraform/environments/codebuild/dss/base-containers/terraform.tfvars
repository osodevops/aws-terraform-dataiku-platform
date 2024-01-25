# AWS region for resources
aws_region = "eu-west-2"

# Name of the VPC subnets to use in building
build_subnet_name_filter = "*Private*"

# Maximum run-time of the build job
build_timeout = 180

# Tags to add to all Terraform resources that support them
common_tags = {
  Application = "CodeBuild"
  Environment = "tooling"
  Function    = "Dataiku AMI building"
  Tooling     = "Terraform"
}

# Size and type of the instance used to build the image.
packer_instance_type = "t3.xlarge"

# Name of the CodeBuild project
project_name = "build-base-containers"

# Owning account of the source image - The account where the DSS Design AMI is available from
source_image_account_no = "YOUR-AWS-ACCOUNT-NUMBER-HERE"

# Repository used to get the ansible and packer build code
source_repository_url = "https://github.com/osodevops/terraform-aws-dataiku-platform"

# Name of the VPC to use for AMI builds
vpc_name = "MY-VPC"

# Vault configuration
# To enable vault as a store for the github token, uncomment vault blocks in these files:
# - provider.tf
# - data.tf
# - main.tf
vault_env      = "MY-VAULT-ENVIRONMENT"
vault_role     = "MY-VAULT-ROLE"
vault_address  = "https://MY-VAULT-URL"
vault_skip_tls = true
