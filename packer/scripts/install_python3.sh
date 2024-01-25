#!/bin/bash -eux

# Install Python 3.
sudo yum -y install python3

#used by some depends in Ansible
sudo ln -s /bin/pip3 /usr/local/bin/pip3
