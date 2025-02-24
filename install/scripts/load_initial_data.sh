#!/bin/sh
source /data/venv/bin/activate
cd /data/deephunter/
python3 manage.py loaddata install/fixtures/authgroup.json
python3 manage.py loaddata install/fixtures/country.json
python3 manage.py loaddata install/fixtures/threatactor.json
python3 manage.py loaddata install/fixtures/threatname.json
python3 manage.py loaddata install/fixtures/vulnerability.json
python3 manage.py loaddata install/fixtures/mitretactic.json
python3 manage.py loaddata install/fixtures/mitretechnique.json
python3 manage.py loaddata install/fixtures/tag.json
python3 manage.py loaddata install/fixtures/targetos.json
python3 manage.py loaddata install/fixtures/query.json
