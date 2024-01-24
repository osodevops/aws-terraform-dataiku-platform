terraform {
  required_version = "~> 1.7.0"

  backend "s3" {
    bucket         = "MY-BUCKET-NAME"
    dynamodb_table = "MY-DYNAMODB-LOCKING-TABLE-tf-state-lock"
    region         = "MY-AWS-REGION"
    key            = "dss/codebuild/design/terraform.tfstate"
    encrypt        = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}