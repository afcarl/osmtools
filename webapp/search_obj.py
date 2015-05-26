#!/usr/bin/env python
import math
import re
import array

def getdist((lat0,lng0),(lat1,lng1)):
    dx = abs(lat0-lat1)*111
    dy = abs(lng0-lng1)*90
    return math.sqrt(dx*dx+dy*dy)

WORDS = re.compile(ur'\w+', re.U)
def getgrams(s):
    for m in WORDS.finditer(s):
        w = m.group(0)
        if len(w) == 1:
            yield w
        else:
            for (c1,c2) in zip(w[:-1],w[1:]):
                yield c1+c2
    return

def search(node, point, entity, lat0, lng0, args, radius=0.005):
    point.execute('SELECT nid,lat,lng FROM point WHERE '
                  '?<=lat and ?<=lng and lat<=? and lng<=?;',
                  (lat0-radius,lng0-radius, lat0+radius,lng0+radius))
    eids = {}
    for (nid,lat1,lng1) in point:
        print (nid,lat1,lng1)
        node.execute('SELECT eid FROM node WHERE nid=?', (nid,))
        for (eid,) in node:
            #print (lat1,lng1), getdist((lat0,lng0),(lat1,lng1)), eid
            if eid in eids: continue
            eids[eid] = (nid,lat1,lng1)
    print (lat0, lng0, eids)
    #
    for name in args:
        for w in getgrams(name.decode('sjis')):
            entity.execute('SELECT eids FROM gram_entity WHERE w=?;', (w,))
            for (b,) in entity:
                a = array.array('I')
                a.fromstring(b)
                for eid in set(eids).difference(a):
                    del eids[eid]
    #
    for (eid,(nid,lat,lng)) in eids.iteritems():
        entity.execute('SELECT name,props FROM entity WHERE eid=?;', (eid,))
        for (name,props) in entity:
            yield (nid,lat,lng,name,props)
    return
