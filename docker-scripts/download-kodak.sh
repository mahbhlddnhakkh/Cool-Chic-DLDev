#!/bin/bash

# https://r0k.us/graphics/kodak/

set -e

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 /path/to/save/"
    exit 1
fi

#for i in {1..24}; do
for i in {1..1}; do # Because I actually need only the first image for my test
    i_mod=$i
    if [ $i -lt 10 ]; then
        i_mod="0$i"
    fi
    echo "kodim$i_mod.png"
    curl "https://r0k.us/graphics/kodak/kodak/kodim$i_mod.png" -o "$1/kodim$i_mod.png"
done
