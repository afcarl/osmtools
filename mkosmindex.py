#!/usr/bin/env python
import sys
import sqlite3
import struct

def main(argv):
    args = argv[1:]
    dstpath = args.pop(0)
    srcpath = args.pop(0)
    dstdb = sqlite3.connect(dstpath)
    srcdb = sqlite3.connect(srcpath)
    src = srcdb.cursor()
    dst = dstdb.cursor()
    #
    nid2tid = {}
    src.execute('SELECT tid,nids FROM way WHERE tid is not NULL;')
    for (tid,b) in src:
        n = len(b)/4
        nids = struct.unpack('<'+'I'*n, b)
        for nid in nids:
            nid2tid[nid] = tid
    print >>sys.stderr, 'nid2tid:', len(nid2tid)
    #
    src.execute('SELECT * FROM node;')
    for (nid,tid,lat,lng) in src:
        if tid is None:
            if nid not in nid2tid: continue
            tid = nid2tid[nid]
        dst.execute('INSERT INTO node VALUES (?,?);', (nid,tid))
        dst.execute('INSERT INTO point VALUES (?,?,?);', (nid,lat,lng))
    dstdb.commit()
    src.execute('SELECT * FROM tag;')
    for (tid,name,yomi) in src:
        dst.execute('INSERT INTO tag VALUES (?,?,?);', (tid,name,yomi))
    dstdb.commit()
    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
