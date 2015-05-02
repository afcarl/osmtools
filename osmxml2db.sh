#!/bin/sh
exec >osmxml2db.log
exec 2>&1
exec </dev/null
renice +20 -p $$
ulimit -m 1000000000
date

sqlite3 osm-tmp.db < osmxml2db.sql
bzip2 -dc osm-src.bz2 | python osmxml2db.py osm-tmp.db
sqlite3 osm-tmp.db < osmxml2db_index.sql

date
