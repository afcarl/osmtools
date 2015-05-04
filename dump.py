#!/usr/bin/env python
import sys
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

# main
def main(argv):
    args = argv[1:]
    fp = file(args.pop(0), 'rb')
    count = {}
    for obj in read_objs(fp):
        #print obj
        (tid,name,yomi,props) = obj
        for (k,v) in props:
            if k not in count: count[k] = 0
            count[k] += 1
    for (k,v) in count.iteritems():
        print v, k.encode('utf-8')
    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
