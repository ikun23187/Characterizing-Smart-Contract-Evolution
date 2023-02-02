#!/bin/bash

if [ $# = 1 ]; then
    strategy=$1
else
    select strategy in MOST_SIMILAR SAME_CONTRACT_NAME SAME_CONTRACT_NAME_AND_CREATOR \
        LONGEST_PATH PAGERANK EARLIEST MOST_REUSE_TIMES; do
            break
    done
    strategy=${strategy:-MOST_SIMILAR}
fi

nohup ./b.py $strategy 0.9 0.8 &> "${strategy}_0.9_0.8.out" &
nohup ./b.py $strategy 0.9 0.7 &> "${strategy}_0.9_0.7.out" &
nohup ./b.py $strategy 0.9 0.6 &> "${strategy}_0.9_0.6.out" &
nohup ./b.py $strategy 0.9 0.5 &> "${strategy}_0.9_0.5.out" &
nohup ./b.py $strategy 0.8 0.7 &> "${strategy}_0.8_0.7.out" &
nohup ./b.py $strategy 0.8 0.6 &> "${strategy}_0.8_0.6.out" &
nohup ./b.py $strategy 0.8 0.5 &> "${strategy}_0.8_0.5.out" &
nohup ./b.py $strategy 0.7 0.6 &> "${strategy}_0.7_0.6.out" &
nohup ./b.py $strategy 0.7 0.5 &> "${strategy}_0.7_0.5.out" &
nohup ./b.py $strategy 0.6 0.5 &> "${strategy}_0.6_0.5.out" &
