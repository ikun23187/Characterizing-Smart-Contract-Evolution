#!/usr/bin/env python3

import csv
import os
import sys

import fasttext as ft
import matplotlib.pyplot as plt
import numpy as np

from scripts.common import *

# load model from model_file
model_file = 'solclone/vectorize/model_sg.bin'
model = ft.load_model(model_file)

# load repo_contracts_info, (addr,name,ver,tid)
repo_contracts_info = 'data/deduplicated_repo_contracts_info.csv'
repo_contracts = {}
with open(repo_contracts_info) as f:
    for addr, name, ver, tid in csv.reader(f):
        if addr not in repo_contracts:
            repo_contracts[addr] = {}
        if name not in repo_contracts[addr]:
            repo_contracts[addr][name] = []
        repo_contracts[addr][name] += [(int(ver), int(tid))]

# load repo_contract_tokens, and then vectorize
repo_contract_tokens = 'data/normalized_tokens_for_each_contract.txt'
repo_vectors = {}
for addr, name, v in zip(*load_data(model, repo_contract_tokens)):
    addr, ver, _ = addr.split('~')
    addr = addr.strip('.').lstrip('\/')
    ver = int(ver)
    repo_vectors[addr, name, ver] = v

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
# add the column `reuse times`
reuse_times_info = 'solclone/data/normalized_tokens_deduplicated.txt'
with open(reuse_times_info) as f:
    reuse_times = [int(n) for _, n in csv.reader(f)]
for tid, (addr, name, creator, bn) in all_contracts.items():
    all_contracts[tid] = (addr, name, creator, bn, reuse_times[tid])
# add the column `pagerank`
pagerank_result = 'data/pagerank.npy'
pageranks = np.load(pagerank_result)
for tid, (addr, name, creator, bn, rt) in all_contracts.items():
    all_contracts[tid] = (addr, name, creator, bn, rt, pageranks[tid])

# load all_contract_tokens, and then vectorize
all_contract_tokens = 'solclone/data/normalized_tokens_for_each_contract.txt'
_, _, all_vectors, *_ = load_data(model, all_contract_tokens, False)

# get similar contracts lazily
def _similar_contracts(vectors, th):
    cached_similar_contracts = {}
    def similar_contracts(tid):
        if tid not in cached_similar_contracts:
            temp = [(t, sim) for t, v in enumerate(vectors) if th <= (sim := similarity(vectors[tid], v)) < 1]
            cached_similar_contracts[tid] = [t for t, _ in sorted(temp, key=lambda tup: tup[1], reverse=True)]
        return cached_similar_contracts[tid]
    return similar_contracts

class longest_path:
    @staticmethod
    def _dig(similar_contracts, similarity, all_contracts, th1, th2):
        def dig(root_tid):
            root_addr, root_name, root_creator, root_bn, root_rt, root_pr = all_contracts[root_tid]
            cached_paths = {}
            def dfs(tid1):
                if tid1 in cached_paths:
                    return cached_paths[tid1]
                height, path = 0, []
                addr1, name1, creator1, bn1, rt1, pr1 = all_contracts[tid1]
                for tid2 in similar_contracts(tid1):
                    if tid2 not in all_contracts:
                        continue
                    addr2, name2, creator2, bn2, rt2, pr2 = all_contracts[tid2]
                    # if bn1 < bn2 and similarity(root_tid, tid2) >= th2:
                    # if bn1 < bn2 and similarity(root_tid, tid2) >= th2 and root_name == name2:
                    if bn1 < bn2 and similarity(root_tid, tid2) >= th2 and root_name == name2 and root_creator == creator2:
                        if (p := dfs(tid2)) and len(p) > height:
                            height, path = len(p), p
                cached_paths[tid1] = path + [tid1]
                return cached_paths[tid1]
            return dfs(root_tid)[::-1]
        return dig

# th1: two nodes are connected when the similarity between them is not less than th1
# th2: the similarity between the root (i.e. root_tid) and each node are not less than th2
def _dig(all_contracts, strategy, th1, th2):
    similar_contracts = _similar_contracts(all_vectors, th1)
    if strategy == 'LONGEST_PATH':
        return longest_path._dig(similar_contracts, lambda tid1, tid2: similarity(all_vectors[tid1], all_vectors[tid2]), all_contracts, th1, th2)
    def dig(root_tid):
        path = []
        root_addr, root_name, root_creator, root_bn, root_rt, root_pr = all_contracts[root_tid]
        root_vec = all_vectors[root_tid]
        curr_tid = root_tid
        while True:
            path += [curr_tid]
            tid1, next_tid, min_bn, max_rt, max_pr = curr_tid, None, float('+inf'), 0, 0
            addr1, name1, creator1, bn1, rt1, pr1 = all_contracts[tid1]
            for tid2 in similar_contracts(tid1):
                if tid2 not in all_contracts:
                    continue
                addr2, name2, creator2, bn2, rt2, pr2 = all_contracts[tid2]
                if bn1 < bn2 and similarity(root_vec, all_vectors[tid2]) >= th2:
                    if strategy == 'MOST_SIMILAR':
                        next_tid = tid2
                        break
                    elif strategy == 'SAME_CONTRACT_NAME':
                        if root_name == name2:
                            next_tid = tid2
                            break
                    elif strategy == 'SAME_CONTRACT_NAME_AND_CREATOR':
                        if root_name == name2 and root_creator == creator2:
                            next_tid = tid2
                            break
                    elif strategy == 'EARLIEST':
                        if bn2 < min_bn:
                            min_bn = bn2
                            next_tid = tid2
                    elif strategy == 'MOST_REUSE_TIMES':
                        if rt2 > max_rt:
                            max_rt = rt2
                            next_tid = tid2
                    elif strategy == 'PAGERANK':
                        # if pr2 > max_pr:
                        if root_name == name2 and pr2 > max_pr:
                            max_pr = pr2
                            next_tid = tid2
                    else:
                        raise Exception('unsupported dig strategy')
            if next_tid is not None:
                curr_tid = next_tid
            else:
                break
        return path
    return dig

def evaluate(strategy, th1, th2):
    dig = _dig(all_contracts, strategy, th1, th2)
    m, tot_precision, tot_recall = 0, 0, 0
    for addr in repo_contracts:
        for name in repo_contracts[addr]:
            vers = repo_contracts[addr][name]
            if len(vers) <= 1:
                continue
            truth = [tid for ver, tid in vers if tid in all_contracts]
            # if len(truth) < len(vers):
            #     print('ERROR', addr, name, len(vers), len(truth))
            if len(truth) == 0:
                continue
            m += 1
            pred = dig(truth[0])
            truth, n = set(truth), 0
            for tid in pred:
                if tid in truth:
                    n += 1
            tot_precision += n / len(pred)
            pred, n = set(pred), 0
            for tid in truth:
                if tid in pred:
                    n += 1
            tot_recall += n / len(truth)
    print(th1, th2, tot_precision / m, tot_recall / m)

if __name__ == '__main__':
    _, strategy, th1, th2, *_ = sys.argv
    evaluate(strategy, float(th1), float(th2))
