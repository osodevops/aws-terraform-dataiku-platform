resource "aws_security_group" "codebuild" {
  name        = "codebuild-${var.project_name}"
  description = "Managed by Terraform"
  vpc_id      = data.aws_vpc.build_vpc.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "TCP"
    self        = true
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    {
      "Name" = "codebuild-${var.project_name}"
    },
  )
}
