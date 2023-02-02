import csv
import pickle

# load gas_result_file, (addr,name,creator,bn,tid,pattern1,pattern2,pattern3,pattern4,pattern6,pattern7), with header
gas_result_file = 'data/gas.csv'
with open(gas_result_file) as f:
    gas_result = {(addr, name): _ for addr, name, creator, bn, tid, *_ in csv.reader(f)}
patterns = gas_result['addr', 'name']

# load all_contracts_info, (addr,name,creator,bn,tid)
all_contracts_info = 'data/deduplicated_contracts_info.csv'
all_contracts = {}
with open(all_contracts_info) as f:
    for addr, name, creator, bn, tid in csv.reader(f):
        bn, tid = int(bn), int(tid)
        if tid not in all_contracts:
            all_contracts[tid] = []
        all_contracts[tid] += [(addr, name, creator, bn)]
for tid, contracts in all_contracts.items():
    all_contracts[tid] = min(contracts, key=lambda tup: tup[-1]) # choose the earliest one

# load paths_file
paths_file = 'data/paths.pkl'
with open(paths_file, 'rb') as f:
    paths = pickle.load(f)

res = {}
for root_tid, path in paths.items():
    n = len(path) - 1
    if n == 0:
        continue
    # print(root_tid, end='')
    res[root_tid] = []
    for i, _ in enumerate(patterns):
        ne, ni, nb, nn = 0, 0, 0, 0
        prev = None
        for tid in path:
            addr, name, creator, bn = all_contracts[tid]
            curr = bool(int(gas_result[addr, name][i]))
            if prev is None:
                prev = curr
                continue
            if prev and (not curr): # become more efficient
                ne += 1
            if (not prev) and curr: # become more inefficient
                ni += 1
            if (not prev) and (not curr): # both efficient
                nb += 1
            if prev and curr: # neither efficient
                nn += 1
            prev = curr
        # print(f',{ne/n},{ni/n},{nb/n},{nn/n}', end='')
        res[root_tid] += [(ne, ni, nb, nn)]
    # print('')
