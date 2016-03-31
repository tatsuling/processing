#!/bin/bash

mkdir -p combined

for x in *.log; do
    echo "Processing ${x}"
    files="${x}"
    if [[ -f ${x}.backup ]]; then
        files="${x}.backup ${x}"
    fi
    ~/bin/gather.py --output=combined/${x}.trace ${files}
done

tar -jcf combined.tar.bz2 combined

