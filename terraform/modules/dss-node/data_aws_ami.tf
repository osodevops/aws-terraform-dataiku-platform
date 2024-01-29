data "aws_ami" "dataiku_dss" {
  most_recent = true

  filter {
    name = "name"

    values = [var.ami_name_filter]
  }

  owners = [local.ami_owner]
}
