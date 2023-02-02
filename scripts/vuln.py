import csv
import pickle

# load vuln_result_file, (addr,name,creator,bn,tid,front_running,unchecked_low_calls,ignore,arithmetic,other,denial_service,reentrancy,time_manipulation,access_control), with header
vuln_result_file = 'data/vuln.csv'
with open(vuln_result_file) as f:
    vuln_result = {(addr, name): _ for addr, name, creator, bn, tid, *_ in csv.reader(f)}
vuln_types = vuln_result['addr', 'name']

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
    for i, vuln_type in enumerate(vuln_types):
        if vuln_type in {'ignore', 'other'}:
            continue
        ns, ni, nb, nn = 0, 0, 0, 0
        prev = None
        for tid in path:
            addr, name, creator, bn = all_contracts[tid]
            curr = bool(int(vuln_result[addr, name][i]))
            if prev is None:
                prev = curr
                continue
            if prev and (not curr): # become more secure
                ns += 1
            if (not prev) and curr: # become more insecure
                ni += 1
            if (not prev) and (not curr): # both secure
                nb += 1
            if prev and curr: # neither secure
                nn += 1
            prev = curr
        # print(f',{ns/n},{ni/n},{nb/n},{nn/n}', end='')
        res[root_tid] += [(ns, ni, nb, nn)]
    # print('')
