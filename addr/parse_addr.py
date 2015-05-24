#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import sqlite3
import re
import reg
import array
from region import EXACT, KEYWORD

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

REGION = Trie()
for (k,v) in EXACT.iteritems():
    REGION.add(k, (True, v))
for (k,v) in KEYWORD.iteritems():
    REGION.add(k, (False, v))

POSTAL = re.compile(r'\d{3}-?\d{4}', re.U)
DIGIT = re.compile(r'\d+', re.U)
WORD = re.compile(r'\w+', re.U)

def reg_name(s):
    def f(m): return str(reg.intkan(m.group(0)))
    s = reg.KANDIGIT.sub(f, s).translate(reg.ALT)
    return s

def get_preds(s):
    i = 0
    while i < len(s):
        m = POSTAL.match(s, i)
        if m:
            v = m.group(0).replace('-','')
            yield [('P', v)]
            i = m.end(0)
            continue
        m = DIGIT.match(s, i)
        if m:
            w = m.group(0)
            yield [('W', w)]
            i = m.end(0)
            continue
        m = WORD.match(s, i)
        if m:
            (k,v) = REGION.lookup(s, i)
            if v is None:
                yield [('W', s[i:])]
                i = m.end(0)
            else:
                (exact,codes) = v
                if exact:
                    yield [('C', codes)]
                else:
                    yield [('C', codes), ('W', k)]
                i += len(k)
            continue
        i += 1
    return

def list_addr(preds):
    def f(i):
        if i < len(preds):
            for z in f(i+1):
                for p1 in preds[i]:
                    yield [p1]+z
        else:
            yield []
    return f(0)

def search_addr(cur, preds):
    #print 'search_addr', preds
    codes = None
    for (t,v) in preds:
        if t == 'C':
            if codes is None:
                codes = set(v)
            else:
                codes.intersection_update(set(v))
    if not codes: return None
    #print 'codes', codes
    aids = None
    for (t,v) in preds:
        ids1 = None
        if t == 'W':
            for g in reg.getgrams(v):
                cur.execute('SELECT aids FROM gram_address WHERE w=?;', (g,))
                for (b,) in cur:
                    a = array.array('I')
                    a.fromstring(b)
                    if ids1 is None:
                        ids1 = set(a)
                    else:
                        ids1.intersection_update(set(a))
            cur.execute('SELECT aid FROM address WHERE rgncode IN (%s);' %
                        ','.join(map(str, codes)))
            if ids1:
                ids1.intersection_update( set( aid for (aid,) in cur ) )
        elif t == 'P':
            cur.execute('SELECT aid FROM address WHERE postal=?;', (v,))
            ids1 = set( aid for (aid,) in cur )
        elif t == 'C':
            continue
        #print 'pred', (t,v), ids1
        if not ids1: break
        if aids is None:
            aids = ids1
        else:
            aids.intersection_update(ids1)
    return aids

def main(argv):
    args = argv[1:]
    path = args.pop(0)
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    #
    s = u'165-0022 東京都中野区江古田'
    s = reg.zen2han(s)
    preds = list(get_preds(s))
    print preds
    for pr in list_addr(preds):
        print pr, search_addr(cur, pr)
    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
