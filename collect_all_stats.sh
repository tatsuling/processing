#!/bin/bash

#declare -a pids

items="standard_32M drowsy_32M gated_32M bayesian_32M"
for x in ${items}; do
	echo "Collecting $x stats."
	~/bin/collect_stats.py *${x}*.yaml | column -t > ${x}.raw.csv
	#pids[${x}]=$!
done

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

