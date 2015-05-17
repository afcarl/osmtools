#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
    d = {}
    def add(k, v):
        if k in d:
            r = d[k]
        else:
            d[k] = r = set()
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
        name = x[-1]
        add(name, (True,rgncode))
        add(name[:-1], (False,rgncode))
    #
    print 'ADDRESS = {'
    for k in sorted(d):
        v = d[k]
        #if len(v) < 2: continue
        codes = set( code for (_,code) in v )
        exacts = set( exact for (exact,_) in v )
        assert len(exacts) == 1
        exact = list(exacts)[0]
        print " (u'%s', %r, %r)," % (k.encode('utf-8'), exact, list(codes))
    print '}'
    return

if __name__ == '__main__': sys.exit(main(sys.argv))
