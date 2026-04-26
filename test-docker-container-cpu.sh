#!/bin/bash

set -e

# https://stackoverflow.com/questions/25292198/docker-how-can-i-copy-a-file-from-an-image-to-a-host

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <image name (likely 'cool-chic')> <path to save (E.g. ~/dataset-tests-res/)>"
    exit 1
fi

date
mkdir -p $2
id=$(docker create $1)
docker start -a $id
#docker cp $id:/code/test/test-workdir/ $2
docker cp $id:/code/dataset-tests-res/ $2
docker rm -v $id
date
