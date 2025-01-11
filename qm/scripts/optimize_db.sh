#!/bin/bash
DBPWD=`grep -A 5 DATABASES /data/deephunter/deephunter/settings.py | grep PASSWORD | grep -oP "(?<=: ').*(?=')"`
/usr/bin/mysqlcheck -u deephunter -p"$DBPWD" -o deephunter
