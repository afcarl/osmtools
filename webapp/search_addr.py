#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import array

from addrdict import TRIERAW


FULLWIDTH = u"　！”＃＄％＆’（）＊＋，\uff0d\u2212．／０１２３４５６７８９：；＜＝＞？" \
            u"＠ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ［＼］＾＿" \
            u"‘ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ｛｜｝"
HALFWIDTH = u" !\"#$%&'()*+,--./0123456789:;<=>?" \
            u"@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_" \
            u"`abcdefghijklmnopqrstuvwxyz{|}"
Z2HMAP = dict( (ord(zc), ord(hc)) for (zc,hc) in zip(FULLWIDTH, HALFWIDTH) )
def zen2han(s):
    return s.translate(Z2HMAP)

KAN2NUM = {
    u'〇':0, u'一':1, u'二':2, u'三':3, u'四':4,
    u'五':5, u'六':6, u'七':7, u'八':8, u'九':9,
    u'十':10, u'百':100, u'千':1000
}
def intkan(s):
    d1 = d2 = 0
    for c in s:
        if c in KAN2NUM:
            i = KAN2NUM[c]
            if i < 10:
                d1 = d1*10+i
            else:
                if d1 == 0:
                    d1 = 1
                d2 += d1*i
                d1 = 0
    return d1+d2

def getgrams(w):
    if len(w) == 1:
        yield w
    else:
        for (c1,c2) in zip(w[:-1],w[1:]):
            yield c1+c2
    return

KANDIGIT = re.compile(u'[〇一二三四五六七八九十]+')
KANALT = dict( (ord(v[0]),v[1]) for v in
            (u'ヶケ', u'ッツ',
             u'澤沢', u'淵渕',
             u'槇槙', u'嶋島',
             u'萬万', u'斎斉',
             u'藪薮', u'阪坂',
             u'櫻桜', u'冶治',
             u'曽曾', u'狹挟',
             u'狭挟'
             ))


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

TRIE = TrieDict(TRIERAW)
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
        self.value = v.replace('-','')
        return
    def __repr__(self):
        return ('<Postal %s-%s>' % (self.value[:3], self.value[3:]))

class PredWord(Pred):
    def __init__(self, w):
        self.word = w.translate(KANALT)
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
            (k,v) = TRIE.lookup(s, i)
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

class AddrNotFound(Exception): pass
class NoRegion(AddrNotFound): pass
class NoWord(AddrNotFound): pass

def search_addr(cur, preds):
    #print 'search_addr:', preds
    codes = None
    postal = None
    word = None
    for pred in preds:
        if isinstance(pred, PredRegion):
            if codes is None:
                codes = set(pred.codes)
            else:
                codes.intersection_update(set(pred.codes))
        elif isinstance(pred, PredPostal):
            postal = pred
        elif isinstance(pred, PredWord):
            word = pred
    if not codes and not postal: raise NoRegion
    if not word and not postal: raise NoWord
    #print 'codes', codes
    aids = None
    for pred in preds:
        if isinstance(pred, PredWord):
            ids1 = None
            for g in getgrams(pred.word):
                cur.execute('SELECT aids FROM gram_address WHERE w=?;', (g,))
                for (b,) in cur:
                    a = array.array('I')
                    a.fromstring(b)
                    if ids1 is None:
                        ids1 = set(a)
                    else:
                        ids1.intersection_update(set(a))
            if ids1:
                if postal is not None:
                    cur.execute('SELECT aid FROM address WHERE aid IN (%s) AND postal="%s";' %
                                (','.join(map(str, ids1)), postal.value))
                else:
                    cur.execute('SELECT aid FROM address WHERE aid IN (%s) AND rgncode IN (%s);' %
                                (','.join(map(str, ids1)), ','.join(map(str, codes))))
                ids1.intersection_update(set( aid for (aid,) in cur ))
            
        elif isinstance(pred, PredPostal):
            cur.execute('SELECT aid FROM address WHERE postal=?;', (postal.value,))
            ids1 = set( aid for (aid,) in cur )
        
        elif isinstance(pred, PredRegion):
            continue
        
        if not ids1: break
        if aids is None:
            aids = ids1
            #print ' first: %r (%d)' % (pred, len(aids))
        else:
            aids.intersection_update(ids1)
            #print ' narrow: %r (%d)' % (pred, len(aids))

    #print ' found:', aids
    return aids

def search(cur, s, maxpreds=10):
    s = zen2han(s)
    def f(m): return str(intkan(m.group(0)))
    s = KANDIGIT.sub(f, s)
    preds = list(get_preds(s))
    #print 'preds:', preds
    for (i,pr) in enumerate(expand_preds(preds)):
        try:
            yield search_addr(cur, pr)
        except AddrNotFound, e:
            yield e
        if maxpreds <= i: break
    return
