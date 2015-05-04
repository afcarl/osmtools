#!/usr/bin/env python
# usage: $ ./plot.py out/osm-index.db 35.7 139.7
import sys
import sqlite3

def main(argv):
    import getopt
    import pygame
    def usage():
        print 'usage: %s [-d] [-r range] [-o out.png] [-s size] file.db lat lng' % argv[0]
        return 100
    try:
        (opts, args) = getopt.getopt(argv[1:], 'dr:o:s:')
    except getopt.GetoptError:
        return usage()
    debug = 0
    radius = 0.01
    outpath = 'out.png'
    fontpath = '/usr/share/fonts/OTF/ipag.ttf'
    size = 800
    for (k, v) in opts:
        if k == '-d': debug += 1
        elif k == '-r': radius = float(v)
        elif k == '-o': outpath = v
        elif k == '-s': size = int(v)
    path = args.pop(0)
    latc = float(args.pop(0))
    lngc = float(args.pop(0))
    conn = sqlite3.connect(path)
    ent = conn.cursor()
    node = conn.cursor()
    point = conn.cursor()
    pygame.font.init()
    point.execute('SELECT nid,lat,lng FROM point WHERE ?<=lat and ?<=lng and lat<=? and lng<=?;',
                  (latc-radius,lngc-radius, latc+radius,lngc+radius))
    ents = {}
    for (nid,lat,lng) in point:
        node.execute('SELECT eid,i FROM node WHERE nid=?', (nid,))
        for (eid,i) in node:
            if eid in ents:
                r = ents[eid]
            else:
                ents[eid] = r = []
            r.append((i,lat,lng))
    img = pygame.Surface((size,size))
    img.fill((255,255,255))
    font = pygame.font.Font(fontpath, 12)
    for (eid,pts) in ents.iteritems():
        r = []
        for (_,lat,lng) in sorted(pts):
            y = int(size*(1.0-(lat-latc)/radius)/2)
            x = int(size*(1.0+(lng-lngc)/radius)/2)
            r.append((x,y))
        cx = sum( x for (x,_) in r )/len(r)
        cy = sum( y for (_,y) in r )/len(r)
        ent.execute('SELECT name,props FROM entity WHERE eid=?;', (eid,))
        for (name,props) in ent:
            if 2 <= len(r):
                pygame.draw.lines(img, (0,200,0), 0, r)
            else:
                img.set_at(r[0], (255,0,0))
            b = font.render(name, 0, (0,0,0))
            (w,h) = b.get_size()
            img.blit(b, (cx-w/2,cy-h/2))
    print len(ents), sum(map(len, ents.itervalues()))
    pygame.image.save(img, outpath)
    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
