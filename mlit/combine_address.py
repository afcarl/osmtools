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
    out = csv.writer(sys.stdout)
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
                (lat,lng) = (float(row[6]), float(row[7]))
                name = row[5]
                out.writerow((pid, cid, name.encode('utf-8'), lat, lng))
        zf.close()
    return

if __name__ == '__main__': sys.exit(main(sys.argv))
