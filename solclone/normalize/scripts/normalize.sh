#!/bin/bash

# normalize 
ls ../data/sols | xargs -I{} echo ../data/sols/{} | xargs -n10000 node index.js ../data/normalized_tokens_for_each_contract.txt

# skip the first two columns: contract_addr contract_name, and merge into single line
cut -d' ' -f3- ../data/normalized_tokens_for_each_contract.txt | tr '\n' ' ' > ../data/normalized_tokens.txt
