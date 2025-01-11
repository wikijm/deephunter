#!/bin/bash

### custom settings
TEMP_FOLDER="/data/tmp"
APP_PATH="/data/deephunter"
VENV_PATH="/data/venv"

###
### Do not change what is below, unless you understand what you are doing
###

# List of django apps for migrations
APPS=(qm extensions reports)

USER=$(grep -oP 'USER_GROUP\s?=\s?"\K[^"]+' $APP_PATH/deephunter/settings.py)
GITHUB_URL=$(grep -oP 'GITHUB_URL\s?=\s?"\K[^"]+' $APP_PATH/deephunter/settings.py)

read -p "About to start upgrade. Press <ENTER> to continue"
echo "[INFO] STARTING UPGRADE..."

# Stop apache2
echo "[INFO] Stopping services..."
sudo systemctl stop apache2
sudo systemctl stop celery
sudo systemctl stop redis-server

# Backup DB (non encrypted)
rm -fR $TEMP_FOLDER/DB
mkdir -p $TEMP_FOLDER/DB
source $VENV_PATH/bin/activate
cd $APP_PATH
$VENV_PATH/bin/python3 manage.py dbbackup -O $TEMP_FOLDER/DB
#leave virtual env
deactivate

# Backup source
echo "[INFO] Backup application..."
rm -fR $TEMP_FOLDER/deephunter
mkdir -p $TEMP_FOLDER
mv $APP_PATH $TEMP_FOLDER

read -p "About to download new version. Press <ENTER> to continue"
# Download new version
echo "[INFO] Downloading new version from github..."
rm -fR $APP_PATH
cd /data
git clone $GITHUB_URL

read -p "About to restore prod settings and files. Press <ENTER> to continue"
# restore prod settings and files
echo "[INFO] Restoring migrations folders and settings..."
for app in ${APPS[@]}
do
    cp -R $TEMP_FOLDER/deephunter/$app/migrations/ $APP_PATH/$app/
done
cp $TEMP_FOLDER/deephunter/deephunter/settings.py $APP_PATH/deephunter/

# Migrate
read -p "About to start DB migrations. Press <ENTER> to continue"
echo "[INFO] Proceeding with DB migrations..."
source $VENV_PATH/bin/activate
cd $APP_PATH/
for app in ${APPS[@]}
do
    ./manage.py makemigrations $app
done
./manage.py migrate

# Leave python virtual env
deactivate
echo "[INFO] DB migrations complete"

# Restore permissions
echo "[INFO] Restoring permissions..."
chmod -R 755 $APP_PATH
touch $APP_PATH/campaigns.log
chmod 666 $APP_PATH/campaigns.log
touch $APP_PATH/static/mitre.json
chmod 666 $APP_PATH/static/mitre.json
chown -R $USER $VENV_PATH
chmod -R 755 $VENV_PATH

# Restart apache2
echo "[INFO] Restarting services..."
sudo systemctl start apache2
sudo systemctl restart redis-server
sudo systemctl restart celery

echo "[INFO] UPGRADE COMPLETE"
echo "[INFO] /!\ Remember to remove the DB backup if no longer needed as it is unencrypted!"
