#!/usr/bin/env bash

# Get tag with ECR details
REGION=$(wget -qO- http://instance-data/latest/meta-data/placement/availability-zone | sed 's/.$//')
INSTANCE_ID=$(wget -qO- http://169.254.169.254/latest/meta-data/instance-id)
ECR_LOCATION=$(aws ec2 describe-tags --region=$REGION --filters "Name=key,Values=DataikuEcrName" "Name=resource-id,Values=$INSTANCE_ID" --query 'Tags[*].Value' --output text)

if [[ -z ${ECR_LOCATION} ]]
then
  echo "Error: Could not find tag "DataikuEcrName" with ECR name"
  exit 1
fi

aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ECR_LOCATION}
