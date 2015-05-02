#!/usr/bin/env python
import sys

def main(argv):
    import fileinput
    import csv
    d = {}
    for row in csv.reader(fileinput.input()):
        k = (row[0], row[1].decode('utf-8'))
        if k in d:
            print >>sys.stderr, 'overwritten:', k
        d[k] = row
    out = csv.writer(sys.stdout)
    for k in sorted(d):
        out.writerow(d[k])
    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
