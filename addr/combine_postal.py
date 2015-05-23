#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# usage: ./combine_postal.py postal.csv address.csv > combined.csv
#
import sys
import csv
import reg

def reg_addr(rgncode, s):
    def f(m): return str(reg.intkan(m.group(0)))
    s = reg.KANDIGIT.sub(f, s).translate(reg.ALT)
    s = reg.AZA.sub(ur'\1', s)
    s = reg.NO.sub(u'', s)
    s = reg.SPC.sub(u'', s)
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
        k = reg_post(rgncode, reg.zen2han(name))
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
