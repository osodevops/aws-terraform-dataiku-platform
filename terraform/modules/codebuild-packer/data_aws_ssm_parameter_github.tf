data "aws_ssm_parameter" "github_oauth_token" {
  name = "/${var.environment}/codebuild/github_personal_access_token"
}
