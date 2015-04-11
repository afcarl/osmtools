#!/usr/bin/env python
import sys
import xml.parsers.expat


##  Primitive
##
class Primitive(object):

    def __init__(self, attrs):
        self.attrs = attrs
        self.tags = []
        return

    def __repr__(self):
        return ('<%s: attrs=%r, tags=%r>' %
                (self.__class__.__name__, self.attrs, self.tags))

    def add_tag(self, attrs):
        assert 'k' in attrs and 'v' in attrs
        k = attrs['k']
        v = attrs['v']
        if k == 'name' or k.startswith('name:'):
            self.tags.append((k, v))
        return

    def dump(self):
        if self.tags:
            tags = ( u'%s=%s' % (k,v) for (k,v) in self.tags )
            print '%s: %s' % (self.__class__.__name__,
                              ', '.join(tags).encode('utf-8'))
        return


##  Node
##
class Node(Primitive):

    pass


##  Way
##
class Way(Primitive):

    def __init__(self, attrs):
        Primitive.__init__(self, attrs)
        self.nodes = []
        return
    
    def add_node(self, attrs):
        self.nodes.append(attrs)
        return


##  Relation
##
class Relation(Primitive):

    def __init__(self, attrs):
        Primitive.__init__(self, attrs)
        self.members = []
        return
    
    def add_member(self, attrs):
        self.members.append(attrs)
        return


##  OSMXMLParser
##
class OSMXMLParser(object):

    def __init__(self):
        self._expat = xml.parsers.expat.ParserCreate()
        self._expat.StartElementHandler = self._start_element
        self._expat.EndElementHandler = self._end_element
        self._expat.CharacterDataHandler = self._char_data
        self.reset()
        return

    def reset(self):
        self._stack = []
        self._obj = None
        self.elemcount = {}
        return

    def feed(self, data):
        self._expat.Parse(data)
        return

    def _start_element(self, name, attrs):
        self._stack.append((name, attrs))
        if name not in self.elemcount:
            self.elemcount[name] = 0
        self.elemcount[name] += 1
        #
        if name == 'tag':
            if isinstance(self._obj, Primitive):
                self._obj.add_tag(attrs)
        elif name == 'nd':
            if isinstance(self._obj, Way):
                self._obj.add_node(attrs)
        elif name == 'member':
            if isinstance(self._obj, Relation):
                self._obj.add_member(attrs)
        elif name == 'node':
            assert self._obj is None
            self._obj = Node(attrs)
        elif name == 'way':
            assert self._obj is None
            self._obj = Way(attrs)
        elif name == 'relation':
            assert self._obj is None
            self._obj = Relation(attrs)
        return
    
    def _end_element(self, name):
        assert self._stack
        (name0,attrs0) = self._stack.pop()
        assert name == name0
        #
        if name in ('node', 'way', 'relation'):
            assert self._obj is not None
            self._obj.dump()
            self._obj = None
        return
    
    def _char_data(self, data):
        #print (data, )
        return

# main
def main(argv):
    import fileinput
    parser = OSMXMLParser()
    for (lineno,line) in enumerate(fileinput.input()):
        try:
            parser.feed(line)
        except Exception, e:
            print >>sys.stderr, (lineno, e)
            raise
        if (lineno%10000) == 0:
            sys.stderr.write('%r\n' % lineno); sys.stderr.flush()
    print >>sys.stderr, parser.elemcount
    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
