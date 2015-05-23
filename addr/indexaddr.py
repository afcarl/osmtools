#!/usr/bin/env python
import sys
import sqlite3
import array
import re
import reg

WORDS = re.compile(ur'\w+', re.U)
def getgrams(s):
    for m in WORDS.finditer(s):
        w = m.group(0)
        if len(w) == 1:
            yield w
        else:
            for (c1,c2) in zip(w[:-1],w[1:]):
                yield c1+c2
    return

def reg_name(s):
    def f(m): return str(reg.intkan(m.group(0)))
    s = reg.DIGIT.sub(f, s).translate(reg.ALT)
    return s

def main(argv):
    args = argv[1:]
    dstpath = args.pop(0)
    dstdb = sqlite3.connect(dstpath)
    #
    postal = {}
    fp_combined = file(args.pop(0), 'rb')
    for line in fp_combined:
        line = line.strip().decode('utf-8')
        if line.startswith('!'): continue
        (rgncode, _, vp, va) = line.split(' ')
        (_,kp) = vp.split(',')
        (ka,_,_) = va.split(',')
        postal[(int(rgncode),ka)] = kp
    fp_combined.close()
    #
    gram = {}
    def add_gram(s, aid):
        for w in getgrams(s):
            if w in gram:
                r = gram[w]
            else:
                gram[w] = r = array.array('I')
            r.append(aid)
    dst = dstdb.cursor()
    aid = 0
    fp_addr = file(args.pop(0), 'rb')
    for line in fp_addr:
        line = line.strip().decode('utf-8')
        (_,rgncode,name,lat,lng) = line.split(',')
        rgncode = int(rgncode)
        lat = float(lat)
        lng = float(lng)
        pp = postal.get((rgncode,name))
        add_gram(name, aid)
        add_gram(reg_name(name), aid)
        aid += 1
        #print (aid,rgncode,name,pp,lat,lng)
        dst.execute('INSERT INTO address VALUES (?,?,?,?,?,?);',
                    (aid,rgncode,name,pp,lat,lng))
        dst.execute('INSERT INTO point VALUES (?,?,?);',
                    (aid,lat,lng))
    dstdb.commit()
    fp_addr.close()
    #
    for (w, aids) in gram.iteritems():
        a = array.array('I', sorted(aids))
        b = buffer(a.tostring())
        dst.execute('INSERT INTO gram_address VALUES (?,?);', (w, b))
    dstdb.commit()
    
    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
