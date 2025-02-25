Settings
########

This is the settings page. Only relevant settings for DeepHunter are reported. For details about Django settings, please refer to the official Django documentation.

DEBUG
*****
- **Type**: Boolean
- **Possible values**: ``True`` or ``False``
- **Description**: Used to display debug information. Can be set to ``True`` in development environement, but always to ``False`` in a production environment.
- **Example**: ``DEBUG = True``

SHOW_LOGIN_FORM
***************
- **Type**: Boolean
- **Possible values**: ``True`` or ``False``
- **Description**: If set to ``True``, a login form with username/password fields will be shown to authenticate. If authentication is exclusively based on AD or PingID, it can be set to ``False``.
- **Example**: ``SHOW_LOGIN_FORM = True``

AUTHLIB_OAUTH_CLIENTS
*********************
- **Type**: Dictionary
- **Description**: Used to provide the PingID settings, for the authentication based on PingID. ``client_kwargs`` is used to specify information about the user, in case of successful authentication, in order to populate the local database.
- **Example**:

.. code-block:: py

	AUTHLIB_OAUTH_CLIENTS = {
		'pingid': {
			'client_id': 'deephunterdev',
			'client_secret': 'aB9cD3eF7gH1iJ2kL0mN4pQ6rS8tU5vWzYxZ3A7bC9dE2fG1hI0jsUQK3lM6nP9q',
			'server_metadata_url': 'https://ping-sso.domains.com/.well-known/openid-configuration',
			'client_kwargs': {'scope': 'openid groups profile email'},
		}
	}

USER_GROUP
**********
- **Type**: string (format should be ``user:group``)
- **Description**: User and group. Used by the deployment script (``qm/script/deploy.py``) to fix permissions.
- **Example**: 

.. code-block:: py
	
	USER_GROUP = "tomnook:users"

GITHUB_URL
**********
- **Type**: string
- **Description**: GitHub URL used by the ``deploy.sh`` script to clone the repo.
- **Example**: 

.. code-block:: py

	GITHUB_URL = "https://token@github.com/myuser/deephunter.git"

LDAP_SERVER
***********
- **Type**: string
- **Description**: LDAP server. Used to connect to the LDAP to gather additional information about a user based on a username (previously gathered by S1 using last logged in user), in the timeline view. To ignore the LDAP connection, set ``LDAP_SERVER`` to an empty string.
- **Example**:

.. code-block:: py

	# Set to empty string if you don't want to get additional user info from AD
	# LDAP_SERVER = ''
	LDAP_SERVER = 'gc.domain.com'
	
LDAP_PORT
*********
- **Type**: integer
- **Description**: LDAP port. Used to connect to the LDAP to gather additional information about a user based on a username (previously gathered by S1 using last logged in user), in the timeline view.
- **Example**:

.. code-block:: py
	
	LDAP_PORT = 636

LDAP_SSL
*********
- **Type**: boolean
- **Possible values**: ``True`` or ``False``
- **Description**: Force the LDAP connection to use SSL. Used to connect to the LDAP to gather additional information about a user based on a username (previously gathered by S1 using last logged in user), in the timeline view.
- **Example**:

.. code-block:: py
	
	LDAP_SSL = True

LDAP_USER
*********
- **Type**: string
- **Format**: ``user@domain``
- **Description**: LDAP user (e.g., a service account). Used to connect to the LDAP to gather additional information about a username (previously gathered by S1 using last logged in user), in the timeline view.
- **Example**:

.. code-block:: py

	LDAP_USER = 'SRV12345@gad.domain.com'

LDAP_PWD
********
- **Type**: string
- **Description**: LDAP password associated to ``LDAP_USER``. Used to connect to the LDAP to gather additional information about a user based on a machine name, in the timeline view.
- **Example**:

.. code-block:: py

	LDAP_PWD = 'Awes0m3#P455w9rD'

LDAP_SEARCH_BASE
****************
- **Type**: string
- **Description**: LDAP search base used to query the LDAP when searching for a user from a machine name. Usually composed of a serie of nested DC values.
- **Example**:

.. code-block:: py

	LDAP_SEARCH_BASE = 'DC=gad,DC=domain,DC=com'

LDAP_ATTRIBUTES
***************
- **Type**: string
- **Description**: LDAP attributes mapping. Expected values returned by the LDAP search should include the username, job title, business unit, office location, country. Depending on your LDAP architecture, fields could have different names. Use this mapping table to specify the corresponding fields.
- **Example**:

.. code-block:: py

	LDAP_ATTRIBUTES = {
		'USER_NAME': 'displayName',
		'JOB_TITLE': 'title',
		'BUSINESS_UNIT': 'division',
		'OFFICE': 'physicalDeliveryOfficeName',
		'COUNTRY': 'co'
	}

CUSTOM_FIELDS
*************
- **Type**: dictionnary
- **Description**: The main dashboard of DeepHunter shows a table with statistics from the last campaign (number of matching events, number of machines, etc.). It is possible to add custom fields (additional columns), that are filtered values to make a break down of the number of matching hosts. For example, if you have defined a specific population for VP in your SentinelOne EDR, you may want to display the corresponding number in a dedicated column. There are up to 3 custom fields. For each, you define a ``name``, a ``description`` and the ``filter`` to apply to the query.
- **Example**:

.. code-block:: py

	CUSTOM_FIELDS = {
		"c1": {
			"name": "VIP",
			"description": "VP",
			"filter": "site.name contains:anycase ('VP', 'Exec')"
			},
		"c2": {
			"name": "GSC",
			"description": "GSC",
			"filter": "site.name contains:anycase 'GSC'"
			},
		"c3": {
			}
		}

DB_DATA_RETENTION
*****************
- **Type**: integer
- **Description**: number of days to keep the data in the local database. Default value: 90.
- **Example**:

.. code-block:: py

	DB_DATA_RETENTION = 90

CAMPAIGN_MAX_HOSTS_THRESHOLD
****************************
- **Type**: integer
- **Description**: Because hostname information is stored in the local database each day (campaigns), for each query, during a given number of days (retention), the database could quickly become too large if no threshold is defined. This threshold allows to define a maximum of hosts that would be stored for each query. Set to 1000 by default, as we may assume that a query that matches more than 1000 endpoints/day is not relevant enough for threat hunting.
- **Example**: 

.. code-block:: py

	CAMPAIGN_MAX_HOSTS_THRESHOLD = 1000

VT_API_KEY
**********
- **Type**: string
- **Description**: VirusTotal API key used for the VirusTotal Hash Checker tool, available from the "Tools" menu. Also used by the "Netview" module to scan the reputation of the public IP addresses.
- **Example**: 

.. code-block:: py

	VT_API_KEY = 'r8h84wc9d2v6fj1n5ya7b0qf32kz3p62m14xd9s75boa01u75c6t8s5l3e9a0f7g'

INSTALLED_APPS
**************
- **Type**: list
- **Description**: List of installed applications (initialized by django). Just make sure new DeepHunter modules are listed at the end (e.g., ``qm``, ``extensions``, ``reports``), and modules you are installing/using are also listed (e.g., ``dbbackup``).
- **Example**: 

.. code-block:: py

	# Application definition
	INSTALLED_APPS = [
		'django.contrib.admin',
		'django.contrib.auth',
		'django.contrib.contenttypes',
		'django.contrib.sessions',
		'django.contrib.messages',
		'django.contrib.staticfiles',
		'django_extensions',
		'dbbackup',
		'django_markup',
		'simple_history',
		'qm',
		'extensions',
		'reports',
	]

ROOT_URLCONF
************
- **Type**: string
- **Description**: Main URL file used by DeepHunter. Default value: ``deephunter.urls``. Do not modify this value.
- **Example**: 

.. code-block:: py
	
	ROOT_URLCONF = 'deephunter.urls'

DATABASES
*********
- **Type**: dictionnary
- **Description**: Database settings. By default, configured to be used with MySQL/MariaDB. Refer to the Django documentation to use other backends.
- **Example**: 

.. code-block:: py

	DATABASES = {
		'default': {
			'ENGINE': 'django.db.backends.mysql',
			'NAME': 'deephunter',
			'USER': 'deephunter',
			'PASSWORD': 'D4t4b453_P455w0rD',
			'HOST': '127.0.0.1',
			'PORT': '3306'
		}
	}

TIME_ZONE
*********
- **Type**: string (``TIME_ZONE``), boolean (``USE_TZ``)
- **Description**: Timezone. Modify depending on where you are located.
- **Example**: 

.. code-block:: py

	TIME_ZONE = 'Europe/Paris'
	USE_TZ = True

STATIC_URL
**********
- **Type**: string
- **Description**: Related and absolute path for the static content (images, documentation, etc.).
- **Example**: 

.. code-block:: py

	STATIC_URL = 'static/'
	STATIC_ROOT = '/data/deephunter/static'


SentinelOne API
***************
- **Type**: string
- **Description**: ``S1_URL`` is the SentinelOne URL for your tenant and is used for any API call to SentinelOne. ``S1_TOKEN`` is the token associated to your API. Notice that tokens expire every month (``S1_TOKEN_EXPIRATION`` is set to 30 days by default) and the new token value should be updated (please use the ``update_s1_token.sh`` script to update your token, because it will take care of updating the renewal date).
- **Example**: 

.. code-block:: py

	S1_URL = 'https://yourtenant.sentinelone.net'
	S1_TOKEN_EXPIRATION = 30
	S1_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'

PROXY
*****
- **Type**: dictionnary
- **Description**: Proxy settings for any Internet communication from DeepHunter, including API calls to S1.
- **Example**: 

.. code-block:: py

	PROXY = {
		'http': 'http://proxy:port',
		'https': 'http://proxy:port'
		}

SentinelOne frontend URL
************************
- **Type**: string
- **Description**: Address and parameters to use to point to SentinelOne frontend from the timeline view. Depending on the interface you have enabled (legacy frontend of new frontend), the URL and parameters are different. Make sure to uncomment the correct settings and comment out the ones to ignore. Notice that ``S1_THREATS_URL`` is dnyamically rendered by the Django view using ``format`` to evaluate the correct hostname. This is why the ``{}`` string appears in the URL.
- **Example**: 

.. code-block:: py
	
	### Legacy frontend
	XDR_URL = 'https://xdr.eu1.sentinelone.net'
	XDR_PARAMS = 'view=edr'
	### New frontend
	#XDR_URL = 'https://tenant.sentinelone.net'
	#XDR_PARAMS = '_categoryId=eventSearch'
	
	### Legacy URL for threats
	#S1_THREATS_URL = #'https://tenant.sentinelone.net/incidents/threats?filter={"computerName__contains":"{}","timeTitle":"Last%203%20Months"}'
	### New URL for threats
	S1_THREATS_URL = 'https://tenant.sentinelone.net/incidents/unified-alerts?_scopeLevel=global&_categoryId=threatsAndAlerts&uamAlertsTable.filters=assetName__FULLTEXT%3D{}&uamAlertsTable.timeRange=LAST_3_MONTHS'

LOGIN_URL
*********
- **Type**: string
- **Description**: URL to redirect to when logging out, or as first page when connecting. Shouldn't be changed.
- **Example**: 

.. code-block:: py

	LOGIN_URL = '/admin/login/'

DBBACKUP
********
- **Type**: dictionnary (``DBBACKUP_STORAGE_OPTIONS``) and string (``DBBACKUP_STORAGE`` and ``DBBACKUP_GPG_RECIPIENT``)
- **Description**: ``DBBACKUP_STORAGE_OPTIONS`` is to specify the location of your backups. ``DBBACKUP_GPG_RECIPIENT`` should be the email address used by GPG for the encryption of the backups. Used by the ``./qm/scripts/backup.sh`` script.
- **Example**: 

.. code-block:: py

	### dbbackup settings (encrypted backups)
	DBBACKUP_STORAGE_OPTIONS = {'location': '/data/backups/'}
	DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
	DBBACKUP_GPG_RECIPIENT = 'email@domain.com'

LOGGING
*******
- **Type**: dictionnary
- **Description**: Used to specify the file used for debugging information (``campaigns.log`` by default).
- **Example**: 

.. code-block:: py

	LOGGING = {
		# The version number of our log
		'version': 1,
		# django uses some of its own loggers for internal operations. In case you want to disable them just replace the False above with true.
		'disable_existing_loggers': False,
		# A handler for WARNING. It is basically writing the WARNING messages into a file called WARNING.log
		'handlers': {
			'file': {
				'level': 'ERROR',
				'class': 'logging.FileHandler',
				'filename': BASE_DIR / 'campaigns.log',
			},
			"console": {"class": "logging.StreamHandler"},
		},
		# A logger for WARNING which has a handler called 'file'. A logger can have multiple handler
		'loggers': {
		   # notice the blank '', Usually you would put built in loggers like django or root here based on your needs
			'': {
				'handlers': ['file'], #notice how file variable is called in handler which has been defined above
				'level': 'ERROR',
				'propagate': True,
			},
		},
	}

AUTO_LOGOUT
***********
- **Type**: dictionary
- **Description**: Used for session expiration (recommended). In case of inactivity, your session should auto-expire and you should be automatically disconnected after some time (defined in minutes with the ``IDLE_TIME`` parameter).
- **Example**: 

.. code-block:: py
	
	# Logout automatically after 1 hour
	AUTO_LOGOUT = {
		'IDLE_TIME': timedelta(minutes=60),
		'REDIRECT_TO_LOGIN_IMMEDIATELY': True,
	}

CELERY
******
- **Type**: string
- **Description**: Defines the address of the Celery broker.
- **Example**: 

.. code-block:: py

	CELERY_BROKER_URL = "redis://localhost:6379"
	CELERY_RESULT_BACKEND = "redis://localhost:6379"
