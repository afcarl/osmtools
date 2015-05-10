#!/usr/bin/env python
import sys
import math
import sqlite3
import re
import array

def getdist((lat0,lng0),(lat1,lng1)):
    dx = abs(lat0-lat1)*111
    dy = abs(lng0-lng1)*90
    return math.sqrt(dx*dx+dy*dy)

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
    import getopt
    def usage():
        print 'usage: %s [-d] [-r range] file.db {lat lng|name}' % argv[0]
        return 100
    try:
        (opts, args) = getopt.getopt(argv[1:], 'dr:')
    except getopt.GetoptError:
        return usage()
    debug = 0
    radius = 0.005
    for (k, v) in opts:
        if k == '-d': debug += 1
        elif k == '-r': radius = float(v)
    path = args.pop(0)
    conn = sqlite3.connect(path)
    if 2 <= len(args):
        lat0 = float(args.pop(0))
        lng0 = float(args.pop(0))
        print (lat0,lng0,radius)
        entity = conn.cursor()
        node = conn.cursor()
        point = conn.cursor()
        point.execute('SELECT nid,lat,lng FROM point WHERE '
                      '?<=lat and ?<=lng and lat<=? and lng<=?;',
                      (lat0-radius,lng0-radius, lat0+radius,lng0+radius))
        eids = set()
        for (nid,lat1,lng1) in point:
            node.execute('SELECT eid FROM node WHERE nid=?', (nid,))
            for (eid,) in node:
                print (lat1,lng1), getdist((lat0,lng0),(lat1,lng1)), eid
                if eid in eids: continue
                eids.add(eid)
                entity.execute('SELECT name,props FROM entity WHERE eid=?;', (eid,))
                for (name,props) in entity:
                    print ' ',name.encode('sjis','ignore'), props
    else:
        gram_entity = conn.cursor()
        entity = conn.cursor()
        for name in args:
            tids = None
            for w in chunk(name.decode('sjis')):
                gram_entity.execute('SELECT tids FROM gram_entity WHERE w=?;', (w,))
                for (b,) in gram_entity:
                    a = array.array('I')
                    a.fromstring(b)
                    if tids is None:
                        tids = set(a)
                    else:
                        tids.intersection_update(set(a))
            for tid in tids:
                entity.execute('SELECT name,props FROM entity WHERE eid=?;', (tid,))
                for (name,props) in entity:
                    print ' ',name.encode('sjis','ignore'), props
    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
