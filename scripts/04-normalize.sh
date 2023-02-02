#!/bin/bash

cd /data/ikun23187/ase/vers

# -regex '[^ ]+\.sol\.~.+~' will filter out paths that contain spaces
find . -type f -regextype awk -regex '[^ ]+\.sol\.~.+~' | sort -t~ -k1,1 -k2,2n \
    | xargs -n10000 node ~/ase/solclone/normalize/index_1.js data/normalized_tokens_for_each_contract.txt

cd - &> /dev/null
