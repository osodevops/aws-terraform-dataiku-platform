aws_region  = "YOUR-AWS-REGION"
common_tags = {
  Application = "Dataiku-DSS"
  Tooling     = "Terraform"
  Component   = "Common S3 buckets"
}

bucket_name_dss_config = "dataiku-dss-config"
bucket_name_ssm_logging = "dataiku-ssm-logs"