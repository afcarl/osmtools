#!/bin/sh
exec >mkosmindex.log
exec 2>&1
exec </dev/null
renice +20 -p $$
date

sqlite3 osm-index.db < mkosmindex.sql
python mkosmindex.py osm-index.db osm-tmp.db 
sqlite3 osm-index.db < mkosmindex_index.sql

date
