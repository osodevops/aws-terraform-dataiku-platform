#!/usr/bin/env bash

# Globals
DATADIR='/data/dataiku'

if [[ $(whoami) != 'dataiku' ]]
then
  echo "# Failure. Please run this script as the dataiku user"
  exit 1
fi

if [[ -z $1 ]]
then
  echo "# Failure: Please provide the DSS version you are moving to"
  exit 1
fi


echo "# Have you created a snapshot of rds and the ebs volume manually? ensure this is done before the upgrade (y/n): "
read action
if [[ $action -eq "y" ]]; then
  echo "Upgrade continued."
  /data/dataiku/bin/dss start
  if [[ $? -ne 0 ]]
  then
    echo "# Upgrade stopped."
    exit 1
  fi
fi

VERSION=$1
SPARK_VERION=$2

cd ~dataiku

# Ensure service is stopped
echo "# Checking if DSS is running"
/data/dataiku/bin/dss status
if [[ $? -eq 0 ]]
then
  echo "# Stopping the DSS service"
  /data/dataiku/bin/dss stop
  if [[ $? -ne 0 ]]
  then
    echo "# Failure: Failed to stop the DSS service"
    exit 1
  fi
fi

# Download package
echo "# Downloading installation package"
wget https://cdn.downloads.dataiku.com/public/studio/${VERSION}/dataiku-dss-${VERSION}.tar.gz
if [[ $? -ne 0 ]]
then
  echo "# Failure: wget exited with a non-zero exit-code"
  exit 1
fi

# Unarchive
echo "# Un-taring and un-zipping package"
tar zxvf dataiku-dss-${VERSION}.tar.gz
if [[ $? -ne 0 ]]
then
  echo "# Failure: Could not un-tar and un-zip package"
  exit 1
fi

# Perform upgrade
echo "# Performing upgrade of DSS"
dataiku-dss-${VERSION}/installer.sh -d ${DATADIR} -u
if [[ $? -ne 0 ]]
then
  echo "# Failure: Upgrade process failed"
  exit 1
fi

# Download Hadoop
echo "# Downloading hadoop"
wget  https://cdn.downloads.dataiku.com/public/studio/${VERSION}/dataiku-dss-hadoop-standalone-libs-generic-hadoop3-${VERSION}.tar.gz
if [[ $? -ne 0 ]]
then
  echo "# Failure: wget exited with a non-zero exit-code"
  exit 1
fi

# Install Hadoop
echo "Installing hadoop"
/data/dataiku/bin/dssadmin install-hadoop-integration -standaloneArchive dataiku-dss-hadoop-standalone-libs-generic-hadoop3-${VERSION}.tar.gz
if [[$? -ne 0]]
then
  echo "# Failure: wget exited with a non-zero exit-code"
  exit 1
fi

# Download Spark
echo "# Downloading spark"
wget https://cdn.downloads.dataiku.com/public/studio/${VERSION}/dataiku-dss-spark-standalone-${VERSION}-${SPARK_VERION}-generic-hadoop3.tar.gz
if [[ $? -ne 0 ]]
then
  echo "# Failure: wget exited with a non-zero exit-code"
  exit 1
fi

# Install Spark
echo "Installing spark"
/data/dataiku/bin/dssadmin install-spark-integration -standaloneArchive dataiku-dss-spark-standalone-${VERSION}-${SPARK_VERION}-generic-hadoop3.tar.gz
if [[$? -ne 0]]
then
  echo "# Failure: wget exited with a non-zero exit-code"
  exit 1
fi

# Restart
echo "# Almost there. Do you want to start the DSS service? (y/n): "
read action
if [[ $action -eq "y" ]]; then
  echo "# Starting the DSS service"
  /data/dataiku/bin/dss start
  if [[ $? -ne 0 ]]
  then
    echo "# Failure: Failed to start the DSS service"
    exit 1
  fi
fi

echo "# Complete. Please ensure you have built an AMI with this version of DSS, and executed Terraform. Then terminate this instance to complete the process"
