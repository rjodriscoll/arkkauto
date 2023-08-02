import sys, csv
from io import StringIO

s=sys.stdin.read()
f = StringIO(s)
reader = csv.reader(f, delimiter=',')
writer = csv.writer(sys.stdout, delimiter=',', quotechar='"', lineterminator='\n', quoting=csv.QUOTE_MINIMAL, escapechar=' ')
cols = None
for row in reader:
    if cols == None:
        cols = len(row)
    while (len(row) < cols):
        row.append('')
    writer.writerow(row)