#!/bin/bash

d=`dirname $0`
mkdir -p combined

for x in *.log; do
    echo "Processing ${x}"
    files=`readlink -f "${x}"`
    if [[ -f ${x}.backup ]]; then
        files="${x}.backup ${x}"
    fi
    of=`readlink -f "combined/${x}"`
    pushd ${d}
    ./gather.py --output="${of}" ${files}
    popd
done

echo "Compressing..."
tar -jcf combined.tar.bz2 combined

