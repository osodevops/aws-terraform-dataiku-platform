#!/usr/bin/env bash

set -exuo pipefail
# Script to wrap the creation of dataiku base containers and push them to ECR

BUILD_TYPE=$1
ECR_REPO=$2

DATAIKU_SCRIPT_HOME=/home/dataiku/dataiku-dss-12.4.1

if [[ -z ${BUILD_TYPE} ]]
then
  echo "Error: A build-type is required as the first argument. e.g. container-exec"
  exit 1
fi

if [[ -z ${ECR_REPO} ]]
then
  echo "Error: An ECR repo is required as the second argument. e.g. 123456789123.dkr.ecr.us-east-1.amazonaws.com/dataiku"
  exit 1
fi

BUILD_FLAGS=""

BASE_IMAGE=""
if [[ -f  /tmp/${BUILD_TYPE}/base_image.txt ]]
then
  BASE_IMAGE_RAW=$(cat /tmp/${BUILD_TYPE}/base_image.txt)
  BASE_IMAGE=${BASE_IMAGE_RAW//[$'\t\r\n']}

  if [[ $BASE_IMAGE != "" ]]
  then
    BUILD_FLAGS="${BUILD_FLAGS} --build-from-image  ${BASE_IMAGE}"
    echo "Using base image ${BASE_IMAGE}"
  fi
fi

if [[ -f  /tmp/${BUILD_TYPE}/docker_fragments_append.txt ]]
then
  BUILD_FLAGS="${BUILD_FLAGS} --dockerfile-append  /tmp/${BUILD_TYPE}/docker_fragments_append.txt"
  echo "Appending docker fragments"
fi

if [[ -f  /tmp/${BUILD_TYPE}/docker_fragments_prepend.txt ]]
then
  BUILD_FLAGS="${BUILD_FLAGS} --dockerfile-prepend  /tmp/${BUILD_TYPE}/docker_fragments_prepend.txt"
  echo "Appending docker fragments"
fi

# Fix error with build-images code
sed -i '{s/compute_source_image\(opts.type, opts.r, opts.cuda, opts.cuda_version\)/compute_source_image\(opts.type, opts.distrib, opts.r, r_major_version, opts.cuda, opts.cuda_version\)/}' $DATAIKU_SCRIPT_HOME/resources/container-exec/build-images.py

cmd="/data/dataiku/bin/dssadmin build-base-image --type $BUILD_TYPE --mode build-push --target-registry ${ECR_REPO} ${BUILD_FLAGS}"
echo "Executing command: ${cmd}"

$cmd
if [[ $? -ne 0 ]]
then
  echo "Error: Container build failed to exit cleanly. Check output for errors"
  exit 1
fi

echo "Job completed successfully"