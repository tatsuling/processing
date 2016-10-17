#!/bin/bash

#declare -a pids

# items="standard_32M drowsy_32M gated_32M bayesian_32M"

predictions="s d g b"
sizes="2M 4M 8M 16M 32M"
technologies="32nm"

dir=`dirname $0`

for p in ${predictions}; do
    for s in ${sizes}; do
        for t in ${technologies}; do
            x="${p}_l2_${s}_${t}_normal"
            echo "Collecting $x stats."
            
            echo "${dir}/collect_stats.py *${x}*.yaml | column -t > ${x}.raw.csv"
            if ! ${dir}/collect_stats.py *${x}*.yaml | column -t > ${x}.raw.csv; then
                exit 1
            fi
            # ~/bin/collect_stats.py *${x}*.yaml | column -t > ${x}.raw.csv
        done
    done
done

# items="s_32M_32nm 
# for x in ${items}; do
# 	echo "Collecting $x stats."
# 	~/bin/collect_stats.py *${x}*.yaml | column -t > ${x}.raw.csv
# 	#pids[${x}]=$!
# done

#for pid in ${pids[*]}; do 
#	echo "Waiting for ${pid}..."
#	wait ${pid}
#done

#sleep 10

~/bin/trial_average.py *.raw.csv


#for x in *.raw.csv; do
	#~/bin/trial_average.py ${x}
#done
#
#~/bin/performance.sh

