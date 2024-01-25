terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.8.0"
    }
    template = {
      source  = "hashicorp/template"
      version = ">= 2.2.0"
    }
  }
}
