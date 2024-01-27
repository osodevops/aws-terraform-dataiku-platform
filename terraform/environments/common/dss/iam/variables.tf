variable "aws_region" {
  description = "AWS region we are managing"
  type        = string
}

variable "common_tags" {
  description = "A collection of common tags to be added to resources."
  type        = map(string)
}

variable "security_group_target_names" {
  description = "List of access security groups to create"
  type        = list(string)
}

variable "vpc_name" {
  description = "Name of the VPC we are operating in"
  type        = string
}