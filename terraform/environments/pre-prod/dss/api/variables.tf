variable "additional_security_groups" {
  description = "List of additional security groups to add to running instances"
  type        = list(string)
  default     = []
}

variable "ami_name_filter" {
  description = "Name matching the AMI to be used for this node. Supports wildcards"
  type        = string
}

variable "ami_owner_account" {
  description = "AWS account ID of the AMI owner. Leave blank if you are not sure, defaults to current account."
  type        = string
  default     = ""
}

variable "api_dynamic_settings_json" {
  description = "Map of configuration items to pass to the api configurator"
  type        = any
  default     = {}
}

variable "asg_desired_capacity" {
  description = "The number of instances for the ASG to create"
  type        = number
  default     = 1
}

variable "asg_max_size" {
  type    = number
  default = 1
}

variable "asg_min_size" {
  type    = number
  default = 0
}

variable "aws_region" {
  description = "The AWS region the bucket is to be created in"
  type        = string
}

variable "cloudwatch_alarm_sns_topic_name" {
  description = "Name of the SNS cloud topic used for cloudwatch alerts"
  type        = string
}

variable "common_tags" {
  description = "A collection of common tags to be added to resources."
  type        = map(string)
}

variable "data_volume_device_name" {
  description = "Name of the device. Generally doesnt need to change"
  type        = string
  default     = "/dev/xvdb"
}

variable "data_volume_encrypt" {
  description = "Whether to encrypt the volume"
  type        = bool
  default     = false
}

variable "data_volume_iops" {
  description = "IOPS attributed to the data volume"
  type        = string
  default     = "100"
}

variable "data_volume_kms_key" {
  description = "Custom KMS key to use"
  type        = string
  default     = ""
}

variable "data_volume_mount_point" {
  description = "Where on the filesystem the volume is mounted"
  type        = string
  default     = "/data"
}

variable "data_volume_size" {
  description = "Size of the data volume to create or resize in GB"
  type        = string
  default     = "100"
}

variable "data_volume_type" {
  description = "Type of data volume to create"
  type = string
  default = "gp3"
}

variable "dlm_target_instance_tag" {
  description = "Provide a map of tags for the DLM to target."
  type        = string
  default     = ""
}

variable "dr_target_instance_tag" {
  description = "Provide a single tag for the lambda to target."
  type        = string
  default     = ""
}

variable "dss_node_type" {
  description = "Type of node to configure"
  type        = string
}

variable "dss_s3_config_bucket" {
  description = "Bucket name where the DSS config is stored"
  type        = string
}

variable "dss_s3_config_key" {
  description = "Key of the config file to use for this node"
  type        = string
}

variable "dss_service_port" {
  description = ""
  type        = string
  default     = "11200"
}

variable "dss_service_protocol" {
  type    = string
  default = "HTTP"
}

variable "environment" {
  description = "Name of the DSS environment we are deploying"
  type        = string
}

variable "instance_allowed_ips" {
  description = "List of internal IP ranges allowed access to the dataiku_dss instances"
  type        = list(string)
  default     = []
}

variable "instance_type" {
  type    = string
  default = "m5.large"
}

variable "lb_additional_security_groups" {
  description = "List of additional security groups to allow access to the load balancer"
  type        = list(string)
  default     = []
}

variable "lb_allowed_ips" {
  description = "List of external IP ranges allowed access to the dataiku_dss ALB"
  type        = list(string)
  default     = []
}

variable "lb_allow_security_groups" {
  description = "List of additional security group names (not IDs) to allow access to the load balancer"
  type        = list(string)
  default     = []
}

variable "lb_certificate_arn" {
  description = "The certificate_arn is the ARN of an ACM or TLS cert to use on this listener"
  type        = string
  default     = ""
}

variable "lb_enable_load_balancer" {
  description = "Whether to deploy a load-balancer for this node, and point it to the ASG"
  type        = bool
  default     = false
}

variable "lb_enable_deletion_protection" {
  description = "Prevent tear-down of the ALB without a force"
  type        = bool
  default     = false
}

variable "lb_health_check_response_code" {
  type    = string
  default = "200"
}

variable "lb_health_check_path" {
  type    = string
  default = "/"
}

variable "lb_health_check_port" {
  type    = string
  default = "11200"
}

variable "lb_health_check_protocol" {
  type    = string
  default = "HTTP"
}

variable "lb_health_check_timeout" {
  type    = number
  default = 15
}

variable "lb_http_port" {
  description = "Port to listen on for plain HTTP requests. Redirected to HTTPS by default"
  type        = string
  default     = "80"
}

variable "lb_https_port" {
  description = "Port to listen on for HTTPS requests"
  type        = string
  default     = "443"
}

variable "lb_internal" {
  description = "Force load-balancers to be internal"
  type        = bool
  default     = false
}

variable "lb_logs_s3_enabled" {
  type    = bool
  default = true
}

variable "lb_logs_s3_prefix" {
  type    = string
  default = "dataiku_dss"
}

variable "lb_log_s3_bucket_name" {
  description = "Name for the S3 bucket for load-balancer log storage"
  type        = string
}

variable "private_subnet_name_filter" {
  description = "Filter to use with 'Name' tag to identity private subnets"
  type        = string
  default     = "Private*"
}

variable "public_subnet_name_filter" {
  description = "Filter to use with 'Name' tag to identity public subnets"
  type        = string
  default     = "Public*"
}

variable "r53_enable_private_zone" {
  description = "Determine if the private zone should be enabled."
  type        = bool
  default     = false
}

variable "r53_enable_public_zone" {
  description = "Determine if the public zone should be enabled."
  type        = bool
  default     = false
}

variable "r53_zone_name" {
  description = "The zone we are configuring e.g. myplace.cloud"
  type        = string
  default     = "cloud"
}

variable "root_volume_size" {
  type    = string
  default = "150"
}

variable "s3_allow_instance_bucket" {
  description = "Allow DSS instance to get and put objects into an S3 bucket"
  type        = bool
  default     = false
}

variable "s3_create_instance_bucket" {
  description = "Create a bucket for general use by the instance. A common practice"
  type        = string
  default     = ""
}

variable "s3_session_logging_bucket_arn" {
  description = "Specify the arn of an existing S3 bucket to capture SSM session logs"
  type        = string
  default     = ""
}

variable "s3_instance_bucket_name" {
  description = "Specify the name of the bucket to allow. Does not imply creating the bucket"
  type        = string
  default     = ""
}

variable "ssh_key_name" {
  description = "The name of an EC2 Key Pair that can be used to SSH to the EC2 Instances in this cluster. Set to null to not associate a Key Pair."
  type        = string
  default     = null
}

variable "vpc_name" {
  description = "Prove the name of the VPC where to deploy dataiku_dss, for exp; PROD-VPC-EUW2"
  type        = string
}
