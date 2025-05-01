#!/bin/bash
source /data/venv/bin/activate
cd /data/deephunter/docs/
rm -fR /data/deephunter/static/html/
make html BUILDDIR=/data/deephunter/static/html
chmod -R 755 /data/deephunter/static/html
