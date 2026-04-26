# Cool-Chic with docker

## Requirements

- Ensure that docker or podman (aliased as docker) is installed with optional CUDA support
- ~2 GBs of free RAM
- ~12 GBs of free disk space
- CUDA GPU ~1 GB of free VRAM (the cpu runtime doesn't work)
- bash (optional, but would be really nice)
- time (~9 mins to build image + ~22 mins to test = ~31 mins on 8 core CPU + 2 GB VRAM and 100 Mbit/s internet)
- r0k.us (for kodak dataset), pypi.org and download.pytorch.org to be available

## Building image

```bash
docker build -t cool-chic .
```

## Creating and running the container

### a. With bash script

GPU (CUDA, fast):
```bash
# Replace `~/dataset-tests-res/` with the directory you want to save the results to
sh test-docker-container-gpu.sh cool-chic ~/dataset-tests-res/
```
CPU (doesn't work):
```bash
# Replace `~/dataset-tests-res/` with the directory you want to save the results to
sh test-docker-container-cpu.sh cool-chic ~/dataset-tests-res/
```

### b. Manually

Basically do the `test-docker-container-gpu.sh` script manually

With CUDA GPU:
```bash
docker create cool-chic --gpus all
```
CPU only (doesn't work):
```bash
docker create cool-chic
```

Copy the printed hash and replace `$id` with the hash (or set the variable with export `export id=<hash>`)

```bash
docker start -a $id
# Replace `~/dataset-tests-res/` with the directory you want to save the results to
docker cp $id:/code/dataset-tests-res/ ~/dataset-tests-res/
docker rm -v $id
```

## Done

You should see `TESTS DONE!` printed in a console. Also you can check the test results at `~/dataset-tests-res/` or other directory you have specified.
