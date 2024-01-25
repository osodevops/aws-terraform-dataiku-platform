data "aws_subnets" "subnets" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.build_vpc.id]
  }

  tags = {
    "Name" = var.subnet_name_filter
  }
}
