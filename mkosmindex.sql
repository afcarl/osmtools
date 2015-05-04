CREATE TABLE entity (eid, name, props);
CREATE TABLE node (nid, eid, i);
CREATE VIRTUAL TABLE point USING rtree (nid, lat, lng);
