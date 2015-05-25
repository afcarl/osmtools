#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# usage: python expand_addr.py city.csv
#
import sys
import re


##  TrieDict
##
class TrieDict(object):
    
    def __init__(self, root):
        self.root = root
        return
    
    def add(self, k, v):
        t0 = self.root
        for c in k[:-1]:
            if c in t0:
                (_,t0) = t0[c]
            else:
                t1 = {}
                t0[c] = (None,t1)
                t0 = t1
        c = k[-1]
        if c in t0:
            (v0,t1) = t0[c]
            assert v0 is None
        else:
            t1 = {}
        t0[c] = (v,t1)
        return
    
    def lookup(self, k, i=0):
        t = self.root
        v = None
        s = u''
        for i in xrange(i, len(k)):
            c = k[i]
            if c not in t: break
            (v,t) = t[c]
            s += c
        return (s,v)

PAT1 = re.compile(ur'^(.+市)$')
PAT2 = re.compile(ur'^(.+市)(.+区)$')
PAT3 = re.compile(ur'^(.+区)$')
PAT4 = re.compile(ur'^(.+郡)(.+[町村])$')
PAT5 = re.compile(ur'^(.+[町村])$')
def parse(city):
    for pat in (PAT1, PAT2, PAT3, PAT4, PAT5):
        m = pat.match(city)
        if m: return m.groups()
    return None

def e(x):
    if isinstance(x, (list,tuple,set)):
        return ','.join( e(y) for y in x )
    elif isinstance(x, unicode):
        return x.encode('utf-8')
    else:
        return str(x)

# main
def main(argv):
    import csv
    import fileinput
    args = argv[1:]
    words = {}
    def add(k, v):
        if k in words:
            r = words[k]
        else:
            words[k] = r = set()
        r.add(v)
        return
    #
    for row in csv.reader(fileinput.input()):
        rgncode = int(row[1])
        pref = row[2].decode('utf-8')
        city = row[3].decode('utf-8')
        assert city, row
        x = parse(city)
        assert x, city
        add(pref, (True,rgncode))
        if not pref.endswith(u'道'):
            add(pref[:-1], (False,rgncode))
        add(city, (True,rgncode))
        for name in x:
            add(name, (True,rgncode))
            add(name[:-1], (False,rgncode))
    #
    REGION = TrieDict({})
    for (k,v) in words.iteritems():
        #if len(v) < 2: continue
        codes = [ code for (_,code) in v ]
        exacts = set( exact for (exact,_) in v )
        assert len(exacts) == 1
        exact = list(exacts)[0]
        if exact:
            REGION.add(k, (True, codes))
        else:
            REGION.add(k, (False, codes))
    print '# -*- coding: utf-8 -*-'
    print 'TRIE = %r' % REGION.root
    return

if __name__ == '__main__': sys.exit(main(sys.argv))
