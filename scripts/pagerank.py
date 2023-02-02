# usage: python3 path/to/this/script data/deduplicated_contracts_info.csv /data/ikun23187/ase/sim/ 0.8 $(ls /data/ikun23187/ase/sim/ | wc -l) 1000 0.85 data/pagerank.npy

import csv
import sys

import numpy as np

verbose = True

def pagerank(mat, *, k: int = 100, d: float = 0.85):
    """PageRank Algorithm

    Parameters
    ----------
    mat : numpy.ndarray
        Input adjacency matrix, where mat[i][j] is 0 or 1 and there is an edge from i to j if and only if mat[i][j] is 1. The `mat` will be preprocessed before starting iterations so you just need to pass an adjacency matrix of the graph without any other preprocessing.
    k : int
        Number of iterations. The default is 100.
    d : float
        Damping factor. The default is 0.85.

    Returns
    -------
    Output vector : numpy.ndarray

    See Also
    --------
    https://en.wikipedia.org/wiki/PageRank
    """
    # preprocess `mat`
    # 1. normalize each row vector
    for i, v in enumerate(mat):
        mat[i] = v / norm if (norm := np.linalg.norm(v, 1)) > 0 else v
    # 2. transpose
    mat = np.transpose(mat)
    # 3. update `mat` using damping factor `d`
    _, n = mat.shape
    mat = d * mat + (1 - d) / n
    # init the output column vector `v` randomly, and then normalize
    v = np.random.rand(n, 1)
    v = v / np.linalg.norm(v, 1)
    # iterate `k` times
    for i in range(k):
        if verbose:
            print(f'{i}/{k}', flush=True)
        v = mat @ v
    # transpose `v` to a row vector
    v = np.transpose(v).reshape(n)
    return v

# get similar contracts lazily
def _similar_contracts(d, th):
    cached_similar_contracts = {}
    def similar_contracts(tid):
        if tid not in cached_similar_contracts:
            cached_similar_contracts[tid] = []
            with open(f'{d}/{tid}.txt') as f:
                for t, sim in csv.reader(f):
                    t, sim = int(t), float(sim)
                    if th <= sim < 1:
                        cached_similar_contracts[tid] += [t]
        return cached_similar_contracts[tid]
    return similar_contracts

def main(all_contracts_info_file, sim_dir, th, maxtid, k, d, output_file):
    bns = {}
    with open(all_contracts_info_file) as f:
        for addr, name, creator, bn, tid in csv.reader(f):
            bn, tid = int(bn), int(tid)
            if tid not in bns:
                bns[tid] = bn
            else:
                bns[tid] = min(bns[tid], bn) # choose the earliest one

    similar_contracts = _similar_contracts(sim_dir, th)

    mat = np.zeros((maxtid, maxtid))
    for i in range(maxtid):
        if verbose:
            print(f'{i}/{maxtid}', flush=True)
        tidi = i + 1
        if tidi not in bns:
            continue
        bni = bns[tidi]
        for tidj in similar_contracts(tidi):
            j = tidj - 1
            if tidj not in bns:
                continue
            bnj = bns[tidj]
            if bni < bnj:
                mat[i][j] = 1

    v = pagerank(mat, k=k, d=d)
    np.save(output_file, v)

if __name__ == '__main__':
    _, all_contracts_info_file, sim_dir, th, maxtid, k, d, output_file, *_ = sys.argv
    main(all_contracts_info_file, sim_dir, float(th), int(maxtid), int(k), float(d), output_file)
