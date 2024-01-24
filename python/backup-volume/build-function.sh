#!/bin/bash

# Build a python zip for lambda and upload it to S3

FUNCTION_NAME="backup-volume"
SRC_PATH="src"

function fail() {
  echo "================="
  echo "Error: $1"
  echo "================="
  exit 1
}

function help() {
  cat << EOF
Usage: build-function.sh [options]

A utility to build a python zip for lambda and upload it to an S3 bucket

Options
-b                 Build a wheel package under "dist"
-h                 This text.
-t                 Execute tests against the source code

EOF
}

function check_python_version() {
  VERSION=$(python --version)
  if [[ ! $VERSION =~ ^Python\ 3\.8\. ]]
  then
    fail "This package requires python 3.8.* but you appear to be using ${VERSION}. Please re-run after selecting this python version"
  fi
}

function execute_tests() {
  echo "Setting up test environment"
  # shellcheck source=service_configurator/test-env.sh
  pipenv install -d
  . test-env.sh

  echo "Running pytest"
  pipenv run pytest
  if [[ $? -ne 0 ]]
  then
    fail "Pytest exited with a non-zero exit-code"
    exit 1
  fi
}

function build_package() {
  echo "Building package"
  pipenv run python -m build
}

function populate_build() {
  echo "Populating build directory"

  if [[ ! -d "build" ]]
  then
    mkdir "build"
  fi

  MYDIR=$PWD
  PACKAGE=$(find  . -name *.whl)
  pipenv run pip install -q --progress-bar off "${PACKAGE}" -t "${MYDIR}/build/${FUNCTION_NAME}" --upgrade

  pipenv lock -r > "${MYDIR}/build/${FUNCTION_NAME}/requirements.txt"

  echo "Installing packages locally"
  cd "${MYDIR}/build/${FUNCTION_NAME}" || fail "Could not change to function build directory"
  pipenv run pip install -q --progress-bar off -r requirements.txt -t . --upgrade

  cd "${MYDIR}" || fail "Could not return to original working directory"
}

function create_zip() {
  echo "Creating zip of function"

  MYDIR=$PWD
  cd "${MYDIR}/build/${FUNCTION_NAME}" || fail "Could not change to function build directory"

  zip -r -q "${MYDIR}/${FUNCTION_NAME}.zip" ./*
  HASH=$(openssl dgst -sha256 -binary "${MYDIR}/${FUNCTION_NAME}.zip" | openssl enc -base64 | sed 's/\\n//g')
  echo -n "${HASH}" > "${MYDIR}/${FUNCTION_NAME}.zip.base64sha256"
  echo "Hash is ${HASH}"

  cd "${MYDIR}" || fail "Error changing to original directory"
  echo "Zip creation complete"
}

function cleanup_builds() {
  echo "Cleaning up builds"
  rm -r build
  echo "Complete"
}

function copy_src() {
  echo "Copying src files"
  if [[ ! -d build/${FUNCTION_NAME} ]]
  then
    mkdir -p build/${FUNCTION_NAME}
  fi
  cp src/* build/${FUNCTION_NAME}/
}


# Defaults
PARAMS=""
EXECUTE_BUILDS="false"
EXECUTE_TESTS="false"
while (( "$#" )); do
  case "$1" in
    -b|--build)
      EXECUTE_BUILDS=true
      shift
      ;;
    -t|--test)
      EXECUTE_TESTS=true
      shift
      ;;
    -h|--help)
      help
      exit 0
      ;;
    -*|--*=) # unsupported flags
      echo "Error: Unsupported flag $1" >&2
      exit 1
      ;;
    *) # preserve positional arguments
      PARAMS="$PARAMS $1"
      shift
      ;;
  esac
done
# set positional arguments in their proper place
eval set -- "$PARAMS"

if [[ -z $FUNCTION_NAME ]]
then
  fail "Please the name of a function"
fi
if [[ ! -d ${SRC_PATH} ]]
then
  fail "Could not find the directory containing function ${FUNCTION_NAME}"
fi

check_python_version
if [[ $EXECUTE_TESTS == "true" ]]
then
  execute_tests
fi
if [[ $EXECUTE_BUILDS == "true" ]]
then
  copy_src
  populate_build
  create_zip
  cleanup_builds
fi
