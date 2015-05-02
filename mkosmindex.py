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
    tid2nid = {}
    nidused = set()
    src.execute('SELECT tid,nids FROM way WHERE tid is not NULL;')
    for (tid,b) in src:
        n = len(b)/4
        nids = struct.unpack('<'+'I'*n, b)
        nidused.update(nids)
        for nid in nids:
            tid2nid[tid] = nid
    src.execute('SELECT tid,nid FROM node WHERE tid is not NULL;')
    for (tid,nid) in src:
        nidused.add(nid)
        tid2nid[tid] = nid
    print >>sys.stderr, 'tid2nid:', len(tid2nid)
    print >>sys.stderr, 'nidused:', len(nidused)
    #
    src.execute('SELECT * FROM node;')
    for (nid,_,lat,lng) in src:
        if nid not in nidused: continue
        dst.execute('INSERT INTO point VALUES (?,?,?);', (nid,lat,lng))
    dstdb.commit()
    src.execute('SELECT * FROM tag;')
    for (tid,name,yomi) in src:
        nid = tid2nid[tid]
        dst.execute('INSERT INTO tag VALUES (?,?,?);', (nid,name,yomi))
    dstdb.commit()
    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
