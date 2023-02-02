#!/bin/bash

input_dir=/data/ikun23187/ase/repos
output_dir=/data/ikun23187/ase/vers

# extract all versions of each repo
for i in {0..19}; do
    j=$((50*i+1))
    for repo in $(ls $input_dir | sed -n "$j,+49p"); do
        dst=$output_dir/$repo
        mkdir -p $dst

        echo "Extracting all versions of repo '$repo' to '$dst' ..."

        cd $input_dir/$repo
        master=$(git branch --show-current)
        k=1
        git log --first-parent --date-order --reverse --pretty=format:%H | while read hash; do
            echo "    extracting version $hash ..."
            git checkout $hash &> /dev/null
            find . -type f -name '*.sol' | xargs -I{} cp --parents {} $dst
            find $dst -type f -name '*.sol' | xargs -I{} mv {} {}.~$k~
            git checkout $master &> /dev/null
            k=$((k+1))
        done
        cd - &> /dev/null
    done &> $i.log &
done
