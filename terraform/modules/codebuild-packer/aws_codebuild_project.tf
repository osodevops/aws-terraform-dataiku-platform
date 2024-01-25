resource "aws_codebuild_project" "builder" {
  name          = var.project_name
  description   = "Managed by Terraform: AMI builder using Packer and Ansible."
  build_timeout = var.build_timeout
  service_role  = aws_iam_role.local_codebuild_role.arn

  artifacts {
    type = "NO_ARTIFACTS"
  }

  environment {
    compute_type                = var.compute_type
    image                       = var.environment_build_image
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"
    privileged_mode             = true

    environment_variable {
      name  = "PACKER_BUILD_VPC_ID"
      value = data.aws_vpc.build_vpc.id
    }
    environment_variable {
      name  = "PACKER_BUILD_SUBNET_FILTER"
      value = var.subnet_name_filter
    }
    environment_variable {
      name  = "PACKER_INSTANCE_PROFILE"
      value = aws_iam_instance_profile.codebuild_ec2_iam_profile.name
    }
    environment_variable {
      name  = "EC2_INSTANCE_TYPE"
      value = var.instance_type
    }
    environment_variable {
      name  = "PACKER_BUILD_REGION"
      value = var.region
    }
    environment_variable {
      name  = "AMI_USERS"
      value = var.shared_ami_users
    }
    environment_variable {
      name  = "PUBLIC_IP_ADDRESS"
      value = "false"
    }
    environment_variable {
      name  = "SOURCE_IMAGE_ACCOUNT_NO"
      value = var.source_image_account_no
    }
    environment_variable {
      name  = "SOURCE_IMAGE_NAME"
      value = var.source_image_name
    }
    environment_variable {
      name  = "SSH_INTERFACE"
      value = "private_ip"
    }
    environment_variable {
      name  = "ROOT_VOLUME_SIZE"
      value = var.root_volume_size
    }
    environment_variable {
      name  = "AWS_REGION"
      value = var.region
    }
    environment_variable {
      name  = "ENCRYPT_ROOT_VOLUME"
      value = var.encrypt_ami
    }
    environment_variable {
      name  = "ENCRYPTION_KEY_ARN"
      value = var.kms_key_arn
    }

    dynamic "environment_variable" {
      for_each = var.additional_build_variables
      content {
        name  = environment_variable.key
        value = environment_variable.value
      }
    }
  }

  source {
    type                = "GITHUB"
    location            = var.source_repository_url
    buildspec           = data.template_file.ami_buildspec.rendered
    git_clone_depth     = "0"
    report_build_status = true
  }

  vpc_config {
    security_group_ids = [aws_security_group.codebuild.id]
    subnets            = data.aws_subnets.subnets.ids
    vpc_id             = data.aws_vpc.build_vpc.id
  }
}

resource "aws_codebuild_source_credential" "github_credential" {
  auth_type   = "PERSONAL_ACCESS_TOKEN"
  server_type = "GITHUB"
  token       = data.aws_ssm_parameter.github_oauth_token.value
}
