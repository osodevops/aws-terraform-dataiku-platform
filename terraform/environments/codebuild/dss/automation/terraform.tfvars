# AWS region for resources
aws_region = "eu-west-2"

# Name of the VPC subnets to use in building
build_subnet_name_filter = "Private*"

# Tags to add to all Terraform resources that support them
common_tags = {
  Application = "CodeBuild"
  Environment = "tooling"
  Function    = "Dataiku AMI building"
  Tooling     = "Terraform"
}

# Size and type of the instance used to build the image.
packer_instance_type = "t3.medium"

# Name of the CodeBuild project
project_name = "build-dss-ami-automation"

# Volume size of the build image
root_volume_size = "40"

# Additional AWS accounts to share the AMI to
shared_ami_users = ""

# Owning account of the source image
source_image_account_no = "amazon"

# Source image to base the DSS node AMI on
source_image_name = "amzn2-ami-hvm-*.*.*.*-*-gp2"

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
