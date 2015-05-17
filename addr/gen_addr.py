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
    if isinstance(x, (list,tuple)):
        return ','.join( e(y) for y in x )
    else:
        return x.encode('utf-8')

# main
def main(argv):
    import csv
    import fileinput
    args = argv[1:]
    d = {}
    for row in csv.reader(fileinput.input()):
        pref = row[2].decode('utf-8')
        city = row[3].decode('utf-8')
        assert city, row
        x = parse(city)
        assert x, city
        k = x[-1][:-1]
        if k in d:
            d[k].append((pref,city))
        else:
            d[k] = [(pref,city)]
    for (k,v) in d.iteritems():
        if len(v) < 2: continue
        print e(k), e(v)
    return

if __name__ == '__main__': sys.exit(main(sys.argv))
