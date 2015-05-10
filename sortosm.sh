#!/bin/sh
exec >sortosm.log
exec 2>&1
exec </dev/null
renice +20 -p $$
date

OSMDB=out/osm.db

sqlite3 $OSMDB <<EOF
CREATE TABLE entity (eid, name, props);
CREATE TABLE node (nid, eid, i);
CREATE VIRTUAL TABLE point USING rtree (nid, lat, lng);
EOF

python sortosm.py $OSMDB tmp/entities.bin tmp/nodes.bin tmp/ways.bin

sqlite3 $OSMDB <<EOF
CREATE INDEX entityi on entity(eid);
CREATE INDEX nodei on node(nid);
EOF

date
