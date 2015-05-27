#!/usr/bin/env python
import sys
import sqlite3
import struct
import marshal

def read_obj(fp):
    z = fp.read(5)
    if not z: raise EOFError
    assert z.startswith('+')
    (n,) = struct.unpack('<xI', z)
    return marshal.loads(fp.read(n))

def read_objs(fp):
    while 1:
        try:
            yield read_obj(fp)
        except EOFError:
            break
    return

def main(argv):
    args = argv[1:]
    dstpath = args.pop(0)
    dstdb = sqlite3.connect(dstpath)
    dst = dstdb.cursor()
    fp_entity = file(args.pop(0), 'rb')
    fp_node = file(args.pop(0), 'rb')
    fp_way = file(args.pop(0), 'rb')
    #
    nid2tid = dstdb.cursor()
    nid2tid.execute('CREATE TABLE nid2tid (nid PRIMARY KEY,tid,i);')
    for (_,tid,nids) in read_objs(fp_way):
        for (i,nid) in enumerate(nids):
            try:
                nid2tid.execute('INSERT INTO nid2tid VALUES (?,?,?);', (nid,tid,i))
            except sqlite3.IntegrityError:
                pass
    nid2tid.execute('CREATE INDEX nid2tidi ON nid2tid(nid);')
    fp_way.close()
    dstdb.commit()
    print >>sys.stderr, 'nid2tid done'
    #
    for (nid,tid,(lat,lng)) in read_objs(fp_node):
        if tid is None:
            nid2tid.execute('SELECT tid,i FROM nid2tid WHERE nid=?;', (nid,))
            for (tid,i) in nid2tid:
                break
            else:
                continue
        dst.execute('INSERT INTO node VALUES (?,?,?);', (nid,tid,i))
        dst.execute('INSERT INTO point VALUES (?,?,?);', (nid,lat,lng))
    fp_node.close()
    nid2tid.execute('DROP TABLE nid2tid;')
    dstdb.commit()
    #
    for (tid,name,props) in read_objs(fp_entity):
        props = dict(props)
        v = None
        for k in ('railway','highway','way'):
            if k in props:
                v = '%s=%s' % (k,props[k])
                break
        dst.execute('INSERT INTO entity VALUES (?,?,?);', (tid,name,v))
    fp_entity.close()
    dstdb.commit()
    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
