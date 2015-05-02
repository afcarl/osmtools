#!/usr/bin/env python
import sys
import csv
from cStringIO import StringIO

# main
def main(argv):
    import re
    import os.path
    import zipfile
    import csv
    args = argv[1:]
    city = {}
    for path in args:
        zf = zipfile.ZipFile(path)
        for name in zf.namelist():
            if not name.lower().endswith('.csv'): continue
            print >>sys.stderr, name
            data = zf.read(name)
            for (i,row) in enumerate(csv.reader(StringIO(data))):
                if i == 0: continue
                row = [ x.decode('cp932','ignore') for x in row ]
                pid = int(row[0])
                cid = int(row[2])
                city[(pid,cid)] = (row[1], row[3])
        zf.close()
    out = csv.writer(sys.stdout)
    for (pid,cid) in sorted(city):
        (pname,cname) = city[(pid,cid)]
        out.writerow((pid, cid, pname.encode('utf-8'), cname.encode('utf-8')))
    return

if __name__ == '__main__': sys.exit(main(sys.argv))
