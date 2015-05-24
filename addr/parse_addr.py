#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import sqlite3
import re
import reg
import time
import array
from region import EXACT, KEYWORD


##  TrieDict
##
class TrieDict(object):
    
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

REGION = TrieDict()
for (k,v) in EXACT.iteritems():
    REGION.add(k, (True, v))
for (k,v) in KEYWORD.iteritems():
    REGION.add(k, (False, v))

POSTAL = re.compile(r'\d{3}-?\d{4}', re.U)
DIGIT = re.compile(r'\d+', re.U)
WORD = re.compile(r'[^\d\W]+', re.U)


##  Pred
##
class Pred(object): pass

class PredRegion(Pred):
    def __init__(self, name, codes):
        self.name = name
        self.codes = codes
        return
    def __repr__(self):
        return ('<Region %r (%d codes)>' % (self.name, len(self.codes)))

class PredPostal(Pred):
    def __init__(self, v):
        self.postal = v.replace('-','')
        return
    def __repr__(self):
        return ('<Postal %s-%s>' % (self.postal[:3], self.postal[3:]))

class PredWord(Pred):
    def __init__(self, w):
        self.word = w.translate(reg.ALT)
        return
    def __repr__(self):
        return ('<Word %r>' % self.word)
    
def get_preds(s):
    i = 0
    while i < len(s):
        m = POSTAL.match(s, i)
        if m:
            yield (PredPostal(m.group(0)),)
            i = m.end(0)
            continue
        m = DIGIT.match(s, i)
        if m:
            w = m.group(0)
            yield (PredWord(w),)
            i = m.end(0)
            continue
        m = WORD.match(s, i)
        if m:
            (k,v) = REGION.lookup(s, i)
            if v is None:
                yield (PredWord(m.group(0)),)
                i = m.end(0)
            else:
                (exact,codes) = v
                if exact:
                    yield (PredRegion(k, codes),)
                else:
                    yield (PredRegion(k, codes), PredWord(k))
                i += len(k)
            continue
        i += 1
    return

def expand_preds(preds):
    def f(i):
        if i < len(preds):
            for z in f(i+1):
                for p1 in preds[i]:
                    yield [p1]+z
        else:
            yield []
    return f(0)

def search_addr(cur, preds):
    print 'search_addr:', preds
    codes = None
    for pred in preds:
        if isinstance(pred, PredRegion):
            if codes is None:
                codes = set(pred.codes)
            else:
                codes.intersection_update(set(pred.codes))
    if not codes: return None
    #print 'codes', codes
    aids = None
    for pred in preds:
        if isinstance(pred, PredWord):
            ids1 = None
            for g in reg.getgrams(pred.word):
                cur.execute('SELECT aids FROM gram_address WHERE w=?;', (g,))
                for (b,) in cur:
                    a = array.array('I')
                    a.fromstring(b)
                    if ids1 is None:
                        ids1 = set(a)
                    else:
                        ids1.intersection_update(set(a))
            if ids1:
                cur.execute('SELECT aid FROM address WHERE aid IN (%s) AND rgncode IN (%s);' %
                            (','.join(map(str, ids1)), ','.join(map(str, codes))))
                ids1.intersection_update(set( aid for (aid,) in cur ))
            
        elif isinstance(pred, PredPostal):
            cur.execute('SELECT aid FROM address WHERE postal=?;', (pred.postal,))
            ids1 = set( aid for (aid,) in cur )
            
        elif isinstance(pred, PredRegion):
            continue
        
        if not ids1: break
        if aids is None:
            aids = ids1
            print ' first: %r (%d)' % (pred, len(aids))
        else:
            aids.intersection_update(ids1)
            print ' narrow: %r (%d)' % (pred, len(aids))
    print ' found:', aids
    return aids

def main(argv):
    args = argv[1:]
    path = args.pop(0)
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    #
    s = u'東京 中野 江古田33'
    s = reg.zen2han(s)
    def f(m): return str(reg.intkan(m.group(0)))
    s = reg.KANDIGIT.sub(f, s)
    preds = list(get_preds(s))
    print 'preds:', preds
    for pr in expand_preds(preds):
        t0 = time.time()
        search_addr(cur, pr)
        t1 = time.time()
        print '  time', int((t1-t0)*1000)
    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
