#!/bin/bash

D=$PWD

cd /data/ikun23187/ase/repos
for repo in *; do
    echo $repo
    cd $repo
    git log --first-parent --date-order --reverse --pretty='format:%h %s' | awk 'BEGIN {i=1} {print i++, $0}' | grep '[Bb][Uu][Gg]\|[Vv][Uu][Ll][Nn]'
    cd - &> /dev/null
done

cd $D
