data "aws_subnets" "private" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.dataiku_dss.id]
  }
  tags = {
    Name = var.private_subnet_name_filter
  }
}
