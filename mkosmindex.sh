#!/bin/sh
exec >mkosmindex.log
exec 2>&1
exec </dev/null
renice +20 -p $$
date

sqlite3 out/osm-index.db < mkosmindex.sql
python mkosmindex.py out/osm-index.db tmp/entities.bin tmp/nodes.bin tmp/ways.bin
sqlite3 out/osm-index.db < mkosmindex_index.sql

date
