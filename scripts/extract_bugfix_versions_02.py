#!/usr/bin/env python3

import csv
import sys

import fasttext as ft
import numpy as np

from common import *

import common
common.verbose = True

# load model from model_file
model_file = 'solclone/vectorize/model_sg.bin'
model = ft.load_model(model_file)

# load data
repo_contract_tokens = 'data/normalized_tokens_for_each_contract.txt'
addrs, names, vectors = load_data(model, repo_contract_tokens)

#
vectors1, ids = {}, [0] * len(vectors)
for i, v in enumerate(vectors):
    v = tuple(v)
    if v not in vectors1:
        vectors1[v] = len(vectors1)
    ids[i] = vectors1[v]
contracts = {}
for i, (addr, name, v)in enumerate(zip(addrs, names, vectors)):
    addr, ver, _ = addr.split('~')
    addr = addr.strip('.').lstrip('/')
    ver, tid = int(ver), int(ids[i])
    if addr not in contracts:
        contracts[addr] = {}
    if name not in contracts[addr]:
        contracts[addr][name] = []
    contracts[addr][name] += [(ver, tid)]

# sort and then deduplicate
if verbose:
    print('sort and then deduplicate', flush=True)
for addr in contracts:
    for name in contracts[addr]:
        contracts[addr][name].sort(key=lambda vertid: vertid[0])
        prevtid, temp = -1, []
        for ver, currtid in contracts[addr][name]:
            if currtid != prevtid:
                temp += [(ver, currtid)]
            prevtid = currtid
        contracts[addr][name] = temp

# load bugfix versions from input_file, extract their previous versions and save to output_file (addr,name,ver1,tid1,ver2,tid2)
if verbose:
    print('extract bugfix evolution, i.e. the versions before and after fixing', flush=True)
_, input_file, output_file, *_ = sys.argv
bugfixs = set()
with open(input_file) as f:
    for line in f:
        line = line.rstrip()
        cols = line.split(' ')
        if len(cols) == 1:
            repo = line
        else:
            ver = int(cols[0])
            bugfixs.add((repo, ver))
with open(output_file, 'w') as f:
    writer = csv.writer(f, lineterminator='\n')
    for addr in contracts:
        repo = addr.split('/')[0]
        for name in contracts[addr]:
            n = len(contracts[addr][name])
            if n <= 1:
                continue
            for i in range(n - 1):
                ver1, tid1 = contracts[addr][name][i]
                ver2, tid2 = contracts[addr][name][i + 1]
                if (repo, ver2) in bugfixs:
                    writer.writerow((addr, name, ver1, tid1, ver2, tid2))

if verbose:
    print('done', flush=True)
