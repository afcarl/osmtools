#!/bin/sh
exec >indexosm.log
exec 2>&1
exec </dev/null
renice +20 -p $$
date

OSMDB=out/osm.db

sqlite3 $OSMDB <<EOF
CREATE TABLE gram_entity (w, tids);
EOF

python indexosm.py $OSMDB tmp/entities.bin

sqlite3 $OSMDB <<EOF
CREATE INDEX gram_entityi on gram_entity(w);
EOF

date
