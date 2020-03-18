#!python

import urllib.request
import urllib.parse
import csv
import re
import datetime
import json
import os

distDir = './dist'

ID4=os.getenv('ID4')

params = urllib.parse.urlencode({'format': 'csv', 'id': ID4})
url = "https://docs.google.com/spreadsheets/d/" + ID4 + "/export?%s" % params
with urllib.request.urlopen(url) as f:
    d = f.read().decode('utf-8')
fout = open('d.csv', 'w')
fout.write(d)
fout.close()

pattern = '^(\d\d*)/(\d\d?)/(\d\d?)\s(\d\d?):(\d\d?):(\d\d?)\s*$'

with open('d.csv', newline='') as csvf:
    dat = csvf.readlines()

dict = {}

for k in dat:
    l = k.strip().split(',')
    if l[0][0:4] == '2020':
        result = re.match(pattern, l[0])
        if result: 
            dt = datetime.datetime(int(result.group(1)), int(result.group(2)),
                                   int(result.group(3)), int(result.group(4)),
                                   int(result.group(5)), int(result.group(6)))
            d = dt.strftime('%Y%m%d')
            t = dt.strftime('%H%M%S')
            if not d in dict:
                dict[d] = {}
            dict[d][t] = (int(l[1]), int(l[2]))

list = []
for k in dict:
  list.append(k)
daylist = sorted(list)

dd = {}
dd['inspections_summary'] = {}
labels = dd['inspections_summary']['labels'] = []
dd['inspections_summary']['data'] = {}
inspections = dd['inspections_summary']['data']['県内'] = []


out = []
for d in daylist:
  list = []
  for k in dict[d]:
    list.append(k)
  timelist = sorted(list)
  ti = timelist[-1]
  labels.append("{}/{}".format(d[4:6], d[6:8])) 
  inspections.append(dict[d][ti][1]) 
  
dd['main_summary'] = {}
dd['main_summary']['attr'] = '検査実施人数' 
dd['main_summary']['value'] = dict[daylist[-1]][ti][0]+dict[daylist[-1]][ti][1]
c = dd['main_summary']['children'] = []
c.append({})
c[0]['attr'] = '陽性患者数' 
c[0]['value'] = dict[daylist[-1]][ti][0]

  #templist = []
  #templist.append(d)
  #templist.append(dict[d][timelist.pop()])
  #print(templist)

os.mkdir(distDir)
fout = open(distDir + '/' + 'data.json', 'w')
json.dump(dd, fout, indent=4, sort_keys=True, ensure_ascii=False)
fout.close()
