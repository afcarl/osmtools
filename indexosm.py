#!/usr/bin/env python
import sys
import sqlite3
import struct
import marshal
import array
import re

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

WORDS = re.compile(ur'\w+', re.U)
def chunk(s):
    for m in WORDS.finditer(s):
        w = m.group(0)
        if len(w) == 1:
            yield w
        else:
            for (c1,c2) in zip(w[:-1],w[1:]):
                yield c1+c2
    return

def main(argv):
    args = argv[1:]
    dstpath = args.pop(0)
    dstdb = sqlite3.connect(dstpath)
    fp_entity = file(args.pop(0), 'rb')
    #
    gram = {}
    for (tid,name,_) in read_objs(fp_entity):
        for w in chunk(name):
            if w in gram:
                r = gram[w]
            else:
                gram[w] = r = array.array('I')
            r.append(tid)
    fp_entity.close()
    #
    dst = dstdb.cursor()
    for (w, tids) in gram.iteritems():
        a = array.array('I', sorted(tids))
        b = buffer(a.tostring())
        dst.execute('INSERT INTO gram_entity VALUES (?,?);', (w, b))
    dstdb.commit()
    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
