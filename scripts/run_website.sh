#!/bin/bash

# run this script in the root of the repo to handle pythonpath correctly
# i.e. do ./scripts/run_website.sh in the root of the repo

source setup.sh
python lunchbot/website.py
