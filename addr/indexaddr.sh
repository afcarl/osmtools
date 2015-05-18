#!/bin/sh
exec >indexaddr.log
exec 2>&1
exec </dev/null
renice +20 -p $$
date

ADDRDB=../out/address.db

sqlite3 $ADDRDB <<EOF
CREATE TABLE address (aid, rgncode, name, postal, lat, lng);
CREATE VIRTUAL TABLE point USING rtree (aid, lat, lng);
CREATE TABLE gram_address (w, aids);
EOF

python indexaddr.py $ADDRDB combined.csv address.csv

sqlite3 $ADDRDB <<EOF
CREATE INDEX addressi on address(aid);
CREATE INDEX addressp on address(postal);
CREATE INDEX gram_addressi on gram_address(w);
EOF

date
