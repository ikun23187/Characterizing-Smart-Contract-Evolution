#!/bin/bash

input_dir=/data/ikun23187/ase/repos
output_dir=/data/ikun23187/ase/vers

for i in {0..19}; do
    j=$((50*i+1))
    for repo in $(ls $output_dir | sed -n "$j,+49p"); do
        prev=/dev/null
        find $output_dir/$repo -type f | sort -t~ -k1,1 -k2,2n | while read curr; do
            echo "cmp -s '$prev' '$curr'"
            if cmp -s "$prev" "$curr"; then
                rm "$curr"
            else
                prev="$curr"
            fi
        done
    done &> $i.log &
done
