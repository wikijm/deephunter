Installation
############

Build the python virtual environment
************************************

It is highly recommended that you install DeepHunter in a python virtual environment. There are several tools to do that (Conda, Poetry, etc). We'll use ``venv``.

We'll assume that you have created a ``/data`` directory and you have write access to it.

.. code-block:: sh
      
   $ sudo apt install python3-venv python3-wheel python3-dev default-libmysqlclient-dev build-essential
   $ sudo apt install pkg-config
   $ cd /data
   $ python3 -m venv venv

In Ubuntu 22.04, it seems that Apache can't acccess the directories, unless you give it proper privileges.

.. code-block:: sh
   
   $ chmod -R 755 /data/
   $ chmod 666 /data/deephunter/campaigns.log

Install the database
********************

.. code-block:: sh

	$ sudo apt install mariadb-server libmariadb-dev
	$ sudo mysql_secure_installation
	$ mysql -u root -p
	mysql> create database deephunter;
	mysql> create user deephunter@localhost identified by 'Awes0meP4ssW0rd';
	mysql> grant all privileges on deephunter.* to deephunter@localhost;
	mysql> \q

Install the python dependencies
*******************************

Enter the virtual environment:

.. code-block:: sh
	
	$ source /data/venv/bin/activate
	(venv) $ pip install -r requirements.txt

Download DeepHunter
*******************
To download DeepHunter, use the following git command:

.. code-block:: sh

	$ cd /data/
	$ git clone https://github.com/sebastiendamaye/deephunter.git

Initialization
**************
See the `settings <settings.html>`_ page.

Initialize the database:

.. code-block:: sh

	$ source /data/venv/bin/activate
	(venv) $ ./manage makemigrations
	(venv) $ ./manage migrate

Load data:

.. code-block:: sh

	(venv) $ ./manage.py loaddata _docs/backup/qm.json

Try to run ``./manage.py runserver`` on default port 8000 and confirm that there is no error

Apache2 mod-wsgi
****************

.. code-block:: sh

	$ sudo apt install apache2 apache2-utils libapache2-mod-wsgi-py3

Enable SSL:

.. code-block:: sh

	$ sudo a2enmod ssl

Enable mod headers

.. code-block:: sh

	$ sudo a2enmod headers

Below line is mandatory because ``dhparam.pem`` is required in ``ssl-params.conf``. Improve your encryption by creating a strong DH Group, and enable Perfect Forward Secrecy.

.. code-block:: sh

	$ sudo openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048
	$ sudo a2enconf ssl-params
	$ sudo a2ensite deephunter-ssl

Restart apache2:

.. code-block:: sh

	$ sudo systemctl restart apache2

Crontab (standard user)
***********************

You can use the crontab in ``qm/scripts/crontab``.

.. code-block:: sh

	# m h  dom mon dow   command
	0  4 * * *      /data/deephunter/qm/scripts/run_campaign.sh
	30 5 * * *      /data/deephunter/qm/scripts/optimize_db.sh
	0  6 * * *      /data/deephunter/qm/scripts/backup.sh

For details about the scripts, see the `scripts page <scripts.html>`_.

Encrypted backups
*****************

.. code-block:: sh

	(venv) $ pip install django-dbbackup
	(venv) $ pip install python-gnupg>=0.5.0

Generate a PGP key and set ``DBBACKUP_GPG_RECIPIENT`` to recipient in ``settings.py``.

Import PGP keys, both public and private.

Encrypt:

.. code-block:: sh

	(venv) $ ./manage.py dbbackup --encrypt

Restore from an encrypted backup:

.. code-block:: sh

	(venv) $ ./manage.py dbrestore --decrypt -i /data/backups/DB-2025-01-01-070002.dump.gpg
	Input Passphrase: ***********
	Are you sure you want to continue? [Y/n] Y

Async tasks: Celery / Redis (message broker)
********************************************

Install the message broker:

.. code-block:: sh

	$ sudo apt update && sudo apt install redis
	$ source /data/venv/bin/activate
	(venv) $ pip install celery
	(venv) $ pip install redis

Modify ``/etc/default/celery`` to fit with your environment. An example is given below.

.. code-block:: sh

	CELERYD_NODES="w1"
	CELERY_BIN="/data/venv/bin/celery"
	CELERY_APP="deephunter"
	CELERYD_MULTI="multi"
	CELERYD_OPTS="--time-limit=3600 --concurrency=3"
	CELERYD_PID_FILE="/var/run/celery/%n.pid"
	CELERYD_LOG_FILE="/var/log/celery/%n%I.log"
	CELERYD_LOG_LEVEL="INFO"
	CELERYD_USER="celery"
	CELERYD_GROUP="celery"
	CELERY_CREATE_DIRS=1

On Ubuntu Server, it seems that the ``/var/run/`` directory is purged at each reboot. To make sure the ``celery`` subdirectory is recreated at each boot, you can create the following file in ``/etc/tmpfiles.d/celery.conf``:

.. code-block:: sh

	d /var/run/celery 0755 celery celery

Now, create the celery user and group.

.. code-block:: sh

	$ sudo groupadd celery
	$ sudo useradd -g celery celery

Fix permissions:

.. code-block:: sh

	$ chmod -R 755 /data
	$ chmod 666 /data/deephunter/campaigns.log 

To start the Celery service automatically, you may want to create a file in ``/etc/systemd/system/celery.service`` as follows:

.. code-block:: sh

	[Unit]
	Description=Celery Service
	After=network.target

	[Service]
	Type=forking
	User=celery
	Group=celery
	EnvironmentFile=/etc/default/celery
	WorkingDirectory=/data/deephunter
	ExecStart=/bin/sh -c '${CELERY_BIN} -A $CELERY_APP multi start $CELERYD_NODES \
		--pidfile=${CELERYD_PID_FILE} --logfile=${CELERYD_LOG_FILE} \
		--loglevel="${CELERYD_LOG_LEVEL}" $CELERYD_OPTS'
	ExecStop=/bin/sh -c '${CELERY_BIN} multi stopwait $CELERYD_NODES \
		--pidfile=${CELERYD_PID_FILE} --logfile=${CELERYD_LOG_FILE} \
		--loglevel="${CELERYD_LOG_LEVEL}"'
	ExecReload=/bin/sh -c '${CELERY_BIN} -A $CELERY_APP multi restart $CELERYD_NODES \
		--pidfile=${CELERYD_PID_FILE} --logfile=${CELERYD_LOG_FILE} \
		--loglevel="${CELERYD_LOG_LEVEL}" $CELERYD_OPTS'
	Restart=always

	[Install]
	WantedBy=multi-user.target

Reload services and enable the new service:

.. code-block:: sh

	$ sudo systemctl daemon-reload
	$ sudo systemctl enable celery.service
	$ sudo systemctl start celery.service
	$ sudo systemctl status celery.service

Install initial data
********************
DeepHunter is shipped with some data (fixtures). To install them, run the following commands:

.. code-block:: sh

	$ source /data/venv/bin/activate
	(venv) $ ./manage.py loaddata fixtures/mitretactic.json
	(venv) $ ./manage.py loaddata fixtures/mitretechnique.json
	(venv) $ ./manage.py loaddata fixtures/tag.json
	(venv) $ ./manage.py loaddata fixtures/targetos.json
	(venv) $ ./manage.py loaddata fixtures/query.json

Notice that you will need to populate some tables yourself (threat actors, threat names, vulnerabilities, etc.) depending on the future queries you will create in DeepHunter. Creating new queries in DeepHunter is explained in the `Usage:admin <usage_admin.html>``_ page.