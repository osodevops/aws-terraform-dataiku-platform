aws_region  = "MY-AWS-REGION"
common_tags = {
  Application = "Dataiku-DSS"
  Tooling     = "Terraform"
  Component   = "iam access roles"
}

# Creates security groups named "<item>-access" for use in cross-node access
security_group_target_names = ["automation", "api", "design", "deployer"]

# The name (not ID) of the VPC we are deploying to
vpc_name = "MY-VPC-NAME"