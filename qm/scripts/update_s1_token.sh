#!/bin/bash

# Check if token is passed as arg
if [ -z "$1" ]; then
  echo "Error: Please provide TOKEN as argument."
  exit 1
fi

SCRIPT_DIR=$(dirname "$(realpath "$0")")
SETTINGS_PATH="$SCRIPT_DIR/../../deephunter/settings.py"
TOKENDATE_PATH="$SCRIPT_DIR/../../static/tokendate.txt"

# Update S1 token in configuration file
sed -i "s/TOKEN = '[^']*'/TOKEN = '$1'/g" $SETTINGS_PATH

# Update token date
echo $(date "+%Y-%m-%d") > $TOKENDATE_PATH

# Restart services
sudo systemctl restart apache2
sudo systemctl restart celery
sudo systemctl restart redis

