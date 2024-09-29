#!/bin/bash

if [ $# -lt 1 ]; then
  echo 1>&2 "$0: not enough arguments. Path to an environment variable file must be provided as argument."
  exit 2
elif [ $# -gt 1 ]; then
  echo 1>&2 "$0: too many arguments. Only the first argument is inferred as the path to an environment variable file; all others are ignored."
fi

ENV_FILE="$1"

echo "Starting application with values loaded from $ENV_FILE" 

set -a
source $ENV_FILE

python run app.py