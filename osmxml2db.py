#!/usr/bin/env python
import sys
import sqlite3
import struct
from osmxmlparser import Node, Way, OSMXMLParser


def getname(tags):
    name = None
    for (k,v) in tags:
        if k == 'name' and name is None:
            name = v
        elif k == 'name:ja':
            name = v
    return name

def getyomi(tags):
    yomi = None
    for (k,v) in tags:
        if k == 'name:ja_rm' and yomi is None:
            yomi = v
        elif k == 'name:ja_kana':
            yomi = v
    return yomi

class Parser(OSMXMLParser):
    
    def __init__(self, conn):
        OSMXMLParser.__init__(self)
        self.cur = conn.cursor()
        self._tid = 0
        return

    def add_tag(self, tags):
        tid = None
        name = getname(tags)
        if name is not None:
            yomi = getyomi(tags)
            self._tid += 1
            tid = self._tid
            self.cur.execute('INSERT INTO tag VALUES (?,?,?);',
                             (tid, name, yomi))
        return tid
    
    def add_object(self, obj):
        if isinstance(obj, Node):
            tid = self.add_tag(obj.tags)
            (lat,lng) = obj.pos
            self.cur.execute('INSERT INTO node VALUES (?,?,?,?);',
                             (obj.nid, tid, lat,lng))
        elif isinstance(obj, Way):
            tid = self.add_tag(obj.tags)
            nids = ''.join( struct.pack('<I', nid) for nid in obj.nodes )
            self.cur.execute('INSERT INTO way VALUES (?,?,?);',
                             (obj.nid, tid, buffer(nids)))
        return
    
    def close(self):
        return

# main
def main(argv):
    import fileinput
    args = argv[1:]
    dbname = args.pop(0)
    conn = sqlite3.connect(dbname)
    parser = Parser(conn)
    for (lineno,line) in enumerate(fileinput.input(args)):
        try:
            parser.feed(line)
        except Exception, e:
            print >>sys.stderr, (lineno, e)
            raise
        if (lineno%10000) == 0:
            sys.stderr.write('%r\n' % lineno); sys.stderr.flush()
    parser.close()
    conn.commit()
    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
