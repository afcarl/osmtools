CREATE TABLE tag (tid PRIMARY KEY, name, yomi);
CREATE TABLE node (nid PRIMARY KEY, tid, x, y);
CREATE TABLE way (wid PRIMARY KEY, tid, nids);
