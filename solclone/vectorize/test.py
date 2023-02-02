#!/usr/bin/env python3

import csv
import sys

import fasttext as ft
import numpy as np

# contract2vec
def vectorize(model, c):
    c = c.rstrip('\n')
    return model.get_sentence_vector(c) * (c.count(' ') + 1)

# calculate the similarity between two contract vectors
def similarity(v1, v2):
    return 1 - np.linalg.norm(v1-v2) / (np.linalg.norm(v1)+np.linalg.norm(v2))

_, model_file, contracts_file, ids_file, distinct_contracts_file, output_dir, *_ = sys.argv
thold, verbose = t if len(_) > 0 and 0 <= (t := float(_[0])) <= 1 else 0, len(_) > 1

# load model from model_file
if verbose:
    print(f'loading model from \'{model_file}\' ...', flush=True)
model = ft.load_model(model_file)

with open(contracts_file) as f:
    if verbose:
        print(f'loading data from \'{contracts_file}\' ...', flush=True)
    addrs, names, vectors = [], [], []
    for line in f:
        addr, name, c = line.split(' ', 2)
        addrs += [addr]
        names += [name]
        vectors += [vectorize(model, c)]

    # deduplicate
    if verbose:
        print('deduplicating ...', flush=True)
    vectors, ids, counts = np.unique(vectors, return_inverse=True, return_counts=True, axis=0)
    with open(ids_file, 'w') as f:
        csv.writer(f, lineterminator='\n').writerows(zip(addrs, names, ids))
    with open(distinct_contracts_file, 'w') as f:
        csv.writer(f, lineterminator='\n').writerows(enumerate(counts))
    if verbose:
        print(f'> deduplicated {len(ids)} contracts to {len(vectors)} distinct contracts', flush=True)

    # calculate similarities pairwise
    if verbose:
        print('calculating similarities pairwise ...', flush=True)
    for i, v1 in enumerate(vectors):
        if verbose:
            print(f'  {i+1:6d}/{len(vectors)}', flush=True)
        with open(f'{output_dir}/{i}.txt', 'w') as f:
            csv.writer(f, lineterminator='\n').writerows(sorted(
                ((j, s) for j, v2 in enumerate(vectors) if (s := similarity(v1, v2)) >= thold),
                key=(lambda tup: tup[-1]),
                reverse=True
            ))

    if verbose:
        print('done', flush=True)
