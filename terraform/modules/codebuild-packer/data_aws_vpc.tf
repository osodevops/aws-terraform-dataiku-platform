data "aws_vpc" "build_vpc" {
  filter {
    name   = "tag:Name"
    values = [var.vpc_name]
  }
}