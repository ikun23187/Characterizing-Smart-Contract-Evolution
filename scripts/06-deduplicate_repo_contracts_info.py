#!/usr/bin/env python3

import csv
import sys

_, input_file, output_file, *_ = sys.argv

# load data from input_file 'data/repo_contracts_info.csv', (path,name,tid)
contracts = {}
with open(input_file) as f:
    for path, name, tid in csv.reader(f):
        addr, ver, _ = path.split('~')
        addr = addr.strip('.').lstrip('\/')
        ver, tid = int(ver), int(tid)
        if addr not in contracts:
            contracts[addr] = {}
        if name not in contracts[addr]:
            contracts[addr][name] = []
        contracts[addr][name] += [(ver, tid)]

# sort and then deduplicate
for addr in contracts:
    for name in contracts[addr]:
        contracts[addr][name].sort(key=lambda vertid: vertid[0])
        prevtid, temp = -1, []
        for ver, currtid in contracts[addr][name]:
            if currtid != prevtid:
                temp += [(ver, currtid)]
            prevtid = currtid
        contracts[addr][name] = temp

# save result to output_file 'data/deduplicated_repo_contracts_info.csv', (addr,name,ver,tid)
maxn, totn, m = 0, 0, 0
with open(output_file, 'w') as f:
    writer = csv.writer(f, lineterminator='\n')
    for addr in contracts:
        for name in contracts[addr]:
            n = len(contracts[addr][name])
            if n <= 1:
                continue
            maxn = max(maxn, n)
            totn += n
            m += 1
            for ver, tid in contracts[addr][name]:
                writer.writerow((addr, name, ver, tid))
avgn = totn / m

print(totn, m, avgn, maxn)
