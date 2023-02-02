#!/bin/bash

NO_PER_PAGE=100

m=1000               # total number of repos
n=$((m/NO_PER_PAGE)) # total number of pages

keywords='contract' # if there are multiple keywords, separate them with '%20', e.g. 'apuzzle%20bash'
language='solidity'

for ((i=1; i<=n; i++)); do
    curl -sS -H 'Accept: application/vnd.github.v3+json' \
        "https://api.github.com/search/repositories?q=$keywords+language:$language&sort=stars&per_page=$NO_PER_PAGE&page=$i" \
        | jq -r '.items[].clone_url' >> repos.txt
done

i=0
cat repos.txt | while read repo; do
    reponame=${repo##*/}
    reponame=${reponame%.git}
    reponame=$(printf '%03d' $i)-${reponame}
    echo $reponame
    git clone $repo /data/ikun23187/ase/repos/$reponame
    i=$((i+1))
done

rm repos.txt
