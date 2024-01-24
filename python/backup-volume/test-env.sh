#!/usr/bin/env bash

export PYTHONPATH=$PYTHONPATH:${PWD}/src
export DYNAMODB_INSTANCE_TABLE="test_table"
export ENVIRONMENT=test
export REGION=eu-west-2
