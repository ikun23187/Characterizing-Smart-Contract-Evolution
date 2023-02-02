import os

import numpy as np

verbose = False

# contract2vec
def vectorize(model, c):
    c = c.rstrip('\n')
    return model.get_sentence_vector(c) * (c.count(' ') + 1)

# calculate the similarity between two contract vectors
def similarity(v1, v2):
    return 1 - np.linalg.norm(v1-v2) / (np.linalg.norm(v1)+np.linalg.norm(v2))

# load data from data_file
def load_data(model, data_file, is_deduplicated=True):
    vectorized_data_file = f'{os.path.splitext(data_file)[0]}.npy'
    if os.path.exists(vectorized_data_file):
        if verbose:
            print(f'loading data from \'{vectorized_data_file}\' ...', flush=True)
        return np.load(vectorized_data_file, allow_pickle=True)
    with open(data_file) as f:
        if verbose:
            print(f'loading data from \'{data_file}\' ...', flush=True)
        addrs, names, vectors = [], [], []
        for line in f:
            addr, name, c = line.split(' ', 2)
            addrs += [addr]
            names += [name]
            vectors += [vectorize(model, c)]
        if is_deduplicated:
            np.save(vectorized_data_file, np.array((addrs, names, vectors), dtype=object))
            return addrs, names, vectors
        # deduplicate only if the data in data_file is not deduplicated
        if verbose:
            print('deduplicating ...', flush=True)
        vectors, ids, counts = np.unique(vectors, return_inverse=True, return_counts=True, axis=0)
        if verbose:
            print(f'> deduplicated {len(ids)} contracts to {len(vectors)} distinct contracts', flush=True)
        np.save(vectorized_data_file, np.array((addrs, names, vectors, ids, counts), dtype=object))
        return addrs, names, vectors, ids, counts
