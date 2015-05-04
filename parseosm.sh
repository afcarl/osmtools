#!/bin/sh
exec >parseosm.log
exec 2>&1
exec </dev/null
renice +20 -p $$
ulimit -m 1000000000
date

bzip2 -dc src/osm-src.osm.bz2 | python parseosm.py tmp/entities.bin tmp/nodes.bin tmp/ways.bin

date
