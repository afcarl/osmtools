#!/usr/bin/env python
import sys
import struct
import marshal
from osmxmlparser import Node, Way, OSMXMLParser

def write_obj(fp, obj):
    b = marshal.dumps(obj)
    fp.write('+'+struct.pack('<I', len(b))+b)
    return

def getname(names):
    name = None
    for (k,v) in names:
        if k == 'name' and name is None:
            name = v
        elif k == 'name:ja':
            name = v
    return name

class Parser(OSMXMLParser):
    
    def __init__(self, fp_entity, fp_node, fp_way):
        OSMXMLParser.__init__(self)
        self.fp_entity = fp_entity
        self.fp_node = fp_node
        self.fp_way = fp_way
        self._tid = 0
        return

    def add_entity(self, names, props):
        tid = None
        name = getname(names)
        if name is not None:
            self._tid += 1
            tid = self._tid
            write_obj(self.fp_entity, (tid, name, props))
        return tid
    
    def add_object(self, obj):
        if isinstance(obj, Node):
            tid = self.add_entity(obj.names, obj.props)
            write_obj(self.fp_node, (obj.nid, tid, obj.pos))
        elif isinstance(obj, Way):
            tid = self.add_entity(obj.names, obj.props+[('way','way')])
            if tid is not None:
                write_obj(self.fp_way, (obj.nid, tid, obj.nodes))
        return
    
    def close(self):
        return

# main
def main(argv):
    import fileinput
    args = argv[1:]
    fp_entity = file(args.pop(0), 'wb')
    fp_node = file(args.pop(0), 'wb')
    fp_way = file(args.pop(0), 'wb')
    parser = Parser(fp_entity, fp_node, fp_way)
    for (lineno,line) in enumerate(fileinput.input(args)):
        try:
            parser.feed(line)
        except Exception, e:
            print >>sys.stderr, (lineno, e)
            raise
        if (lineno%10000) == 0:
            sys.stderr.write('%r\n' % lineno); sys.stderr.flush()
    parser.close()
    fp_entity.close()
    fp_node.close()
    fp_way.close()
    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
