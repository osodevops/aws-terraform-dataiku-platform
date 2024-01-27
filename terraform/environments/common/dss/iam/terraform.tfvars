aws_region  = "MY-AWS-REGION"
common_tags = {
  Application = "Dataiku-DSS"
  Tooling     = "Terraform"
  Component   = "iam access roles"
}

security_group_target_names = ["automation", "api", "design"]
