#!/usr/bin/env python
import sys
import math
import sqlite3

def getdist((lat0,lng0),(lat1,lng1)):
    dx = abs(lat0-lat1)*111
    dy = abs(lng0-lng1)*90
    return math.sqrt(dx*dx+dy*dy)

def main(argv):
    import getopt
    def usage():
        print 'usage: %s [-d] [-r range] file.db lat lng' % argv[0]
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
    lat0 = float(args.pop(0))
    lng0 = float(args.pop(0))
    print (lat0,lng0,radius)
    conn = sqlite3.connect(path)
    tag = conn.cursor()
    node = conn.cursor()
    point = conn.cursor()
    point.execute('SELECT nid,lat,lng FROM point WHERE ?<=lat and ?<=lng and lat<=? and lng<=?;',
                  (lat0-radius,lng0-radius, lat0+radius,lng0+radius))
    tids = set()
    for (nid,lat1,lng1) in point:
        node.execute('SELECT tid FROM node WHERE nid=?', (nid,))
        for (tid,) in node:
            print (lat1,lng1), getdist((lat0,lng0),(lat1,lng1)), tid
            if tid in tids: continue
            tids.add(tid)
            tag.execute('SELECT name,yomi FROM tag WHERE tid=?;', (tid,))
            for (name,yomi) in tag:
                print ' ',name.encode('sjis','ignore')
    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
