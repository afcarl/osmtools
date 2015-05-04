#!/usr/bin/env python
import xml.parsers.expat


##  Primitive
##
class Primitive(object):

    def __init__(self, attrs):
        if 'id' in attrs:
            self.nid = int(attrs['id'])
        else:
            self.nid = None
        self.attrs = attrs
        self.names = []
        self.props = []
        return

    def __repr__(self):
        return ('<%s: attrs=%r, tags=%r>' %
                (self.__class__.__name__, self.attrs, self.tags))

    def add_tag(self, attrs):
        assert 'k' in attrs and 'v' in attrs
        k = attrs['k']
        v = attrs['v']
        if k == 'name' or k.startswith('name:'):
            self.names.append((k, v))
        else:
            self.props.append((k, v))
        return


##  Node
##
class Node(Primitive):

    def __init__(self, attrs):
        Primitive.__init__(self, attrs)
        self.pos = None
        if 'lat' in attrs and 'lon' in attrs:
            self.pos = (float(attrs['lat']),
                        float(attrs['lon']))
        return
    

##  Way
##
class Way(Primitive):

    def __init__(self, attrs):
        Primitive.__init__(self, attrs)
        self.nodes = []
        return
    
    def add_node(self, attrs):
        if 'ref' in attrs:
            self.nodes.append(int(attrs['ref']))
        return


##  Relation
##
class Relation(Primitive):

    def __init__(self, attrs):
        Primitive.__init__(self, attrs)
        self.members = []
        return
    
    def add_member(self, attrs):
        if 'ref' in attrs:
            self.members.append(int(attrs['ref']))
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
        return

    def feed(self, data):
        self._expat.Parse(data)
        return

    def add_object(self, obj):
        raise NotImplementedError

    def _start_element(self, name, attrs):
        self._stack.append((name, attrs))
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
            self.add_object(self._obj)
            self._obj = None
        return
    
    def _char_data(self, data):
        #print (data, )
        return
