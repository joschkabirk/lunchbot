#!/bin/bash

# run this script in the head of the repo to handle pythonpath correctly

source .env
source /venv_container/bin/activate
export PYTHONPATH=$PWD:$PYTHONPATH

python lunchbot/website.py