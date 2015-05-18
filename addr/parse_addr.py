#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import sqlite3
import re
import reg
from addr import EXACT, KEYWORD

POSTAL = re.compile(r'^\d{3}-?\d{4}')

class Trie(object):
    
    def __init__(self):
        self.root = {}
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
    
    def lookup(self, k):
        t = self.root
        v = None
        s = u''
        for c in k:
            if c not in t: break
            (v,t) = t[c]
            s += c
        return (s,v)

trie = Trie()
for (k,v) in EXACT.iteritems():
    trie.add(k, (True, v))
for (k,v) in KEYWORD.iteritems():
    trie.add(k, (False, v))

def reg_name(s):
    def f(m): return str(reg.intkan(m.group(0)))
    s = reg.DIGIT.sub(f, s).translate(reg.ALT)
    return s

def parse_addr(db, s):
    s = reg_name(s)
    if POSTAL.match(s):
        pass
    (k,(exact,codes)) = trie.lookup(s)

    return

def main(argv):
    args = argv[1:]
    path = args.pop(0)
    db = sqlite3.connect(path)
    #
    parse_addr(db, u'東京都中野区')
    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
