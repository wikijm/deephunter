Scripts
#######

DeepHunter is shipped with some scripts, located under the ``./qm/scripts/`` folder.

- **backup.sh**: used to do encrypted backups of the database and delete old backups (older than 3 months by default).
- **campaign.py**: daily campaigns script, started from ``run_campaign.sh``. It relies on the ``runscript`` command of the ``django-extensions`` package.
- **crontab**: not a script. Example of crontab.
- **optimize_db.sh**: script to optimize the database after the ``run_campaign.sh`` script is executed.
- **run_campaign.sh**: launcher for running "dynamic" threat hunting analytics and daily campaigns script.
- **upgrade.sh**: script that you can use to upgrade DeepHunter when a new version is available on GitHub.
- **vulnerable_driver_name_detected_loldriver.py**: Script of the dynamic threat hunting analytic called ``vulnerable_driver_name_detected_loldriver.py``. It relies on the ``runscript`` command of the ``django-extensions`` package.
