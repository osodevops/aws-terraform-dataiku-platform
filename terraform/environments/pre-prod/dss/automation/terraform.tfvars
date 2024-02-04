###################################################
# General settings
###################################################

aws_region = "YOUR-AWS-REGION"

# Set of tags to apply to all resources managed by Terraform
common_tags = {
  Application = "Dataiku"
  Environment = "pre-prod"
  Tooling     = "Terraform"
  Function    = "Dataiku - DSS node"
}

# Defines the type of node we are building. Don't change this unless you know what you're doing
dss_node_type = "automation"

# DSS configuration source S3 bucket and key
dss_s3_config_bucket = "MY-S3-BUCKET"
dss_s3_config_key    = "CONFIGURATION-OBJECT-KEY"

# Name of the environment we are deploying. e.g. staging, pre-prod
environment = "pre-prod"


###################################################
# VPC
###################################################

# String and wildcards for finding the private subnets in your VPC
private_subnet_name_filter = "*Private*"

# String and wildcards for finding the public subnets in your VPC
public_subnet_name_filter = "*Public*"

# The name (not ID) of the VPC we are deploying to
vpc_name = "MY-VPC-NAME"


###################################################
# Instance configuration
###################################################

# Set the size of the data volume in GB. If you change this value for an existing deployment, only increase it as decreasing will lead to data-loss
data_volume_size = "200"

# AWS volume type for the data volume
data_volume_type = "gp3"

# Specify IOPS for volume types that support it
data_volume_iops = "1000"

# Where to mount the volume on the OS - Changing this value will require changing related settings in the AMI build
data_volume_mount_point = "/data"

# Whether to encrypt the volumes with the default KMS key
data_volume_encrypt = true

# Instance type for the node
instance_type = "m5.large"

# Size of the root volume in GB
root_volume_size = "150"

# Optionally specify the name of the pre-existing ssh key to configure on the instance
ssh_key_name = ""

# Backup the instance via DLM. Specify a tag matching the one defined in "dlm_target_instance_tag" in the "disaster-recovery" wrapper
dlm_target_instance_tag = "DLMSnapshot"

# Backup the instance via real-time DR mechanism. Specify a tag matching the one defined in "dr_target_instance_tag" in the "disaster-recovery" wrapper
dr_target_instance_tag = "DRSnapshot"


###################################################
# ASG configuration
###################################################

# AMI to select for this node. By default, AMIs generated by this module are named `dss-[node type]-node-[datestamp]`
# The latest available AMI is selected
ami_name_filter = "dss-automation-node-*"

# Where AMIs are owned by another AWS account, specify that account number.
# Leaving blank to use the current account number
ami_owner_account = "AWS-ACCOUNT-NUMBER-OWNING-THE-AMI"

# Provide the names (not the IDs) of any additional security groups to attach to running instances
additional_security_groups = []

# Set the number of nodes created. Valid values are 0 and 1 (multiple nodes of the same type are not currently supported)
asg_desired_capacity = 1

# For CloudWatch alarms, provide a pre-existing SNS topic as an alerting target
cloudwatch_alarm_sns_topic_name = "MY-SNS-TOPIC"

# List of additional IPs to allow access to the node
instance_allowed_ips = []

# Optionally specify the ARN of a pre-existing bucket used to store SSM sessions to the instance
s3_session_logging_bucket_arn = ""

###################################################
# Load-balancer settings
###################################################

# Whether to define the load-balancer resources. If set to false, the node will be "headless", and the following "lb_" settings will be ignored
lb_enable_load_balancer = true

# Additional IP CIDRs to allow access to the load balancer
lb_allowed_ips = []

# Provide the names (not the IDs) of any additional security groups to allow in to the load-balancer
lb_allow_security_groups = ["design-access"]

# Arn of a valid certificate that will be attached to the load-balancer
lb_certificate_arn = ""

# Whether to prevent deletion of the load-balancer. ie terraform destroy will fail unless forced
lb_enable_deletion_protection = false

# Define the primary port served from the load balancer
lb_https_port = 443

# Whether the load-balancer should be internal or external
lb_internal = true

# Should load-balancer access be logged to an S3 bucket. Provide the name of a bucket to create
lb_logs_s3_enabled    = false
lb_log_s3_bucket_name = ""

# Create route53 entries for your node. Zone can be public, private, or both
r53_enable_private_zone = true
r53_enable_public_zone  = false
r53_zone_name           = "MY-ROUTE53-ZONE-NAME"

###################################################
# Additional S3 bucket
###################################################

# Allow the instances access to a pre-existing S3 bucket for storing user data and workflows
s3_allow_instance_bucket = false
s3_instance_bucket_name  = ""

# Optionally create a new bucket instead of using a pre-existing one
s3_create_instance_bucket = false
