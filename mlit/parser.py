#!/usr/bin/env python
import sys
import xml.parsers.expat


##  Parser
##
class Parser(object):
    
    def __init__(self):
        self.pos = {}
        self.name = {}
        self._state = 0
        self._expat = xml.parsers.expat.ParserCreate()
        self._expat.StartElementHandler = self._start_element
        self._expat.EndElementHandler = self._end_element
        self._expat.CharacterDataHandler = self._char_data
        return

    def feed(self, data):
        self._expat.Parse(data)
        return
    
    def get(self):
        for (k,(x,y)) in self.pos.iteritems():
            name = self.name[k]
            yield (name,(x,y))
        return
    
    def _start_element(self, name, attrs):
        #print 'start', name, attrs
        if name == 'jps:GM_Point':
            self.id = attrs['id']
            self._state = 1
        elif self._state == 1 and name == 'DirectPosition.coordinate':
            self._state = 2
        elif name == 'ksj:FB01':
            self._state = 3
        elif self._state == 3 and name == 'ksj:POS':
            self.idref = attrs['idref']
        elif self._state == 3 and name in ('ksj:NA0','ksj:NA8'):
            self._state = 4
        elif self._state == 3 and name == 'ksj:AAC':
            self._state = 5
        return
    
    def _end_element(self, name):
        if name == 'ksj:FB01':
            self.name[self.idref] = (self._name1, self._cid)
        elif self._state == 2:
            self._state = 0
        elif self._state == 4:
            self._state = 3
        elif self._state == 5:
            self._state = 3
        return
    
    def _char_data(self, data):
        #print 'char', len(data)
        if self._state == 2:
            (lat,lng) = data.split(' ')
            self.pos[self.id] = (lat,lng)
            #print (float(x), float(y))
        elif self._state == 4:
            self._name1 = data
            #print (data,)
        elif self._state == 5:
            self._cid = int(data)
            #print (data,)
        return


# main
def main(argv):
    import re
    import os.path
    import zipfile
    import csv
    pat = re.compile(r'P\d\d-\d\d_\d\d.xml')
    args = argv[1:]
    out = csv.writer(sys.stdout)
    for path in args:
        zf = zipfile.ZipFile(path)
        for name in zf.namelist():
            if not pat.match(os.path.basename(name)): continue
            print >>sys.stderr, name
            data = zf.read(name)
            p = Parser()
            p.feed(data)
            for ((name,cid),(lat,lng)) in p.get():
                row = (cid,name.encode('utf-8'),lat,lng)
                out.writerow(row)
        zf.close()
    return

if __name__ == '__main__': sys.exit(main(sys.argv))
