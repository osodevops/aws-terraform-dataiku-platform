#!/usr/bin/env bash

# Prevent the dataiku-configurator from running
touch /var/run/configure-dataiku.lock

# Stop the dataiku service from starting
systemctl dataiku disable
systemctl dataiku stop
