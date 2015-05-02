CREATE TABLE tag (nid, name, yomi);
CREATE VIRTUAL TABLE point USING rtree (nid, x, y);
