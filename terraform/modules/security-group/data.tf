data "aws_vpc" "target" {
  filter {
    name   = "tag:Name"
    values = [var.vpc_name]
  }
}
