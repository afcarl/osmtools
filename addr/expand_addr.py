#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# usage: python expand_addr.py city.csv
#
import sys
import re

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
    EXACT = {}
    KEYWORD = {}
    for (k,v) in words.iteritems():
        #if len(v) < 2: continue
        codes = set( code for (_,code) in v )
        exacts = set( exact for (exact,_) in v )
        assert len(exacts) == 1
        exact = list(exacts)[0]
        if exact:
            EXACT[k] = list(codes)
        else:
            KEYWORD[k] = list(codes)
    
    def show(d, name):
        print '%s = {' % name
        for k in sorted(d):
            v = d[k]
            print " u'%s': %r," % (k.encode('utf-8'), v)
        print '}\n'
        return
    show(EXACT, 'EXACT')
    show(KEYWORD, 'KEYWORD')
    return

if __name__ == '__main__': sys.exit(main(sys.argv))
