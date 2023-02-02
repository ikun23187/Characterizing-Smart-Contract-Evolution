#!/bin/bash

cd ~/ase/
./scripts/extract_bugfix_versions_02.py <(./scripts/extract_bugfix_versions_01.sh) bugfix_versions.csv
awk -F, 'BEGIN {i=1} {print i++ "," $1 ".~" $3 "~"; print i++ "," $1 ".~" $5 "~"}' bugfix_versions.csv > bugfix_versions_mapping.csv
mkdir bugfix_contracts/
awk -F, '{system("cp /data/ikun23187/ase/vers/" $2 " bugfix_contracts/" $1 ".sol")}' bugfix_versions_mapping.csv
