#!/usr/bin/env python3

import csv
import sys

import fasttext as ft
import numpy as np

from common import *

_, model_file, repo_contract_tokens, all_contract_tokens, output_file, *_ = sys.argv
verbose = len(_) > 0

import common
common.verbose = verbose

# load model from model_file
model = ft.load_model(model_file)

# load data
addrs, names, vectors1 = load_data(model, repo_contract_tokens)
_, _, vectors2, *_ = load_data(model, all_contract_tokens, False)

#
if verbose:
    print('#', flush=True)
tids = {tuple(v2): tid for tid, v2 in enumerate(vectors2)}
with open(output_file, 'w') as f:
    csv.writer(f, lineterminator='\n').writerows(
        (addr, name, tids[v]) for addr, name, v1 in zip(addrs, names, vectors1) if (v := tuple(v1)) in tids
    )

if verbose:
    print('done', flush=True)
