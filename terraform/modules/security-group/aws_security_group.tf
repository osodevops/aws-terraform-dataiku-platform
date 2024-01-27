resource "aws_security_group" "access" {
  name        = "${var.target_name}-access"
  description = "Grants access to another service"
  vpc_id      = data.aws_vpc.target.id

  tags = {
    "Name" = "${var.target_name}-access"
  }
}
