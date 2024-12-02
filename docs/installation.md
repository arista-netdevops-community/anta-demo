<!--
  ~ Copyright (c) 2024 Arista Networks, Inc.
  ~ Use of this source code is governed by the Apache License 2.0
  ~ that can be found in the LICENSE file.
  -->

# Lab Installation

## Python

> **info**
> It is recommended to install everything in a Python virtual environment.

It installs the following packages:

- `eos-downloader`: download cEOS image to build topology
- `anta`: ANTA package

```bash
# Python base
pip install -r requirements.txt
```

> **Note**
> If you are running this demo into ATD, then you are good to go with [the demos](../README.md#available-demos)

## Containerlab

Containerlab is engine to run test topology and must be installed prior to launch cEOS instances.

### Linux (recommended)

```bash
# download and install the latest release (may require sudo)
bash -c "$(curl -sL https://get.containerlab.dev)"
```

### OSX

```bash
CLAB_WORKDIR=${PWD}

docker run --rm -it --privileged \
    --network host \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v /run/netns:/run/netns \
    --pid="host" \
    -w $CLAB_WORKDIR \
    -v $CLAB_WORKDIR:$CLAB_WORKDIR \
    ghcr.io/srl-labs/clab bash
```

> [!NOTE]
> Full installation notes on [containerlab website](https://containerlab.dev/install/)
