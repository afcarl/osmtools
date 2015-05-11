#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# usage: ./combine_postal.py postal.csv address.csv > combined.csv
#
import sys
import csv
import re

FULLWIDTH = u"　！”＃＄％＆’（）＊＋，\uff0d\u2212．／０１２３４５６７８９：；＜＝＞？" \
            u"＠ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ［＼］＾＿" \
            u"‘ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ｛｜｝"
HALFWIDTH = u" !\"#$%&'()*+,--./0123456789:;<=>?" \
            u"@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_" \
            u"`abcdefghijklmnopqrstuvwxyz{|}"
Z2HMAP = dict( (ord(zc), ord(hc)) for (zc,hc) in zip(FULLWIDTH, HALFWIDTH) )
def zen2han(s):
    return s.translate(Z2HMAP)

KANDIGIT = {
    u'〇':0, u'一':1, u'二':2, u'三':3, u'四':4,
    u'五':5, u'六':6, u'七':7, u'八':8, u'九':9,
    u'十':10, u'百':100, u'千':1000
}
def intkan(s):
    d1 = d2 = 0
    for c in s:
        if c in KANDIGIT:
            i = KANDIGIT[c]
            if i < 10:
                d1 = d1*10+i
            else:
                if d1 == 0:
                    d1 = 1
                d2 += d1*i
                d1 = 0
    return d1+d2

DIGIT = re.compile(u'[〇一二三四五六七八九十]+')
ALT = dict( (ord(v[0]),v[1]) for v in
            (u'ヶケ', u'ッツ',
             u'澤沢', u'淵渕',
             u'槇槙', u'嶋島',
             u'萬万', u'斎斉',
             u'藪薮', u'阪坂',
             u'櫻桜', u'冶治',
             u'曽曾', u'狹挟',
             u'狭挟'
             ))
AZA = re.compile(u'大?字(.)')
NO = re.compile(u'[ノの]')
SPC = re.compile(u'\s', re.U)
PAREN = re.compile(u'\([^\)]+\)')

def reg_addr(rgncode, s):
    def f(m): return str(intkan(m.group(0)))
    s = DIGIT.sub(f, s).translate(ALT)
    s = AZA.sub(ur'\1', s)
    s = NO.sub(u'', s)
    s = SPC.sub(u'', s)
    return s

def reg_post(rgncode, s):
    if s == u'以下に掲載がない場合':
        return u''
    else:
        s = PAREN.sub(u'', s)
        s = reg_addr(rgncode, s)
        return s

def e(x):
    if isinstance(x, tuple):
        return ','.join( e(y) for y in x )
    else:
        return x.encode('utf-8')

def combine(rgncode, post, addr):
    r = []
    for (ip,(kp,vp)) in enumerate(post):
        for (ia,(ka,va)) in enumerate(addr):
            if kp.startswith(ka) or ka.startswith(kp):
                np = len(kp)
                na = len(ka)
                score = min(np,na)/float(max(np,na))
                r.append((score,ip,ia))
    r.sort(key=lambda (score,_1,_2):score, reverse=True)
    taken_p = set()
    taken_a = set()
    for (_,ip,ia) in r:
        if ia in taken_a: continue
        (kp,vp) = post[ip]
        (ka,va) = addr[ia]
        taken_p.add(ip)
        taken_a.add(ia)
        if kp:
            print rgncode, e(kp)+'/'+e(kp), e(vp), e(va)
        else:
            print '! unmatched', e((ka,va))
    for (ip,(kp,vp)) in enumerate(post):
        if ip in taken_p: continue
        print '! remain_post', e((kp,vp))
    for (ia,(ka,va)) in enumerate(addr):
        if ia in taken_a: continue
        print '! remain_addr', e((ka,va))
    return

def main(argv):
    args = argv[1:]

    postal = {}
    fp_p = file(args.pop(0), 'r')
    for row in csv.reader(fp_p):
        rgncode = int(row[0])
        if rgncode in postal:
            r = postal[rgncode]
        else:
            postal[rgncode] = r = []
        name = row[8].decode('sjis')
        k = reg_post(rgncode, zen2han(name))
        r.append((k,(name,row[2])))
    fp_p.close()

    address = {}
    fp_a = file(args.pop(0), 'r')
    for row in csv.reader(fp_a):
        rgncode = int(row[1])
        if rgncode in address:
            r = address[rgncode]
        else:
            address[rgncode] = r = []
        name = row[2].decode('utf-8')
        k = reg_addr(rgncode, zen2han(name))
        r.append((k,(name,row[3],row[4])))
    fp_a.close()

    for rgncode in sorted(postal.iterkeys()):
        if rgncode not in address: continue
        post = postal[rgncode]
        addr = address[rgncode]
        combine(rgncode, post, addr)
    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
