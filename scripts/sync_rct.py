import json
from collections import defaultdict

import random

source_path = '../data/rct_dump_20150609.json'

input = open(source_path,'r')

raw = json.load(input)

data = defaultdict(dict)

for item in raw:
    data[item['model']][item['pk']] = item.copy()

models = data.keys()
print
for k,v in data['rct.provider'].items():
    pass
    #print v['fields']['name']

samples = []
for m in models:
    k = data[m].keys()
    i = random.choice(k)
    try:
        samples.append(data[m][i])
    except KeyError:
        print "*** no sample for %s ***" % m
for s in samples:
    print 'Model: ', s['model']
    print 'Fields: ', s['fields'].keys()
    print 'All keys: ', s.keys()
    print
    
    #p1 = data['rct.provider'][1]
    #print 
    #print p1['fields'].keys()




