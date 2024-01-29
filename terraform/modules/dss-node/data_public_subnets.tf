data "aws_subnets" "public" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.dataiku_dss.id]
  }
  tags = {
    Name = var.public_subnet_name_filter
  }
}