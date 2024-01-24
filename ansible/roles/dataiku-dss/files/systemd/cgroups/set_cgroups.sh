#!/usr/bin/env bash

# Run as root
# Configures cgroups for the dataiku user
# Launched via a systemd service

mkdir /sys/fs/cgroup/memory/DSS
chown -R dataiku:dataiku /sys/fs/cgroup/memory/DSS

mkdir /sys/fs/cgroup/cpu/DSS
chown -R dataiku:dataiku /sys/fs/cgroup/cpu/DSS