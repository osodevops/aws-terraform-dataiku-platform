data "aws_vpc" "dataiku_dss" {
  filter {
    name   = "tag:Name"
    values = [var.vpc_name]
  }
}