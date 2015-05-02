CREATE TABLE tag (tid, name, yomi);
CREATE TABLE node (nid, tid);
CREATE VIRTUAL TABLE point USING rtree (nid, lat, lng);
