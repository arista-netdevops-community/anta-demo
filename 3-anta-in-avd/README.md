<!--
  ~ Copyright (c) 2024 Arista Networks, Inc.
  ~ Use of this source code is governed by the Apache License 2.0
  ~ that can be found in the LICENSE file.
  -->

# ANTA in AVD

## Overview

TODO

## Preparation

> **Note**
> if you have just finished lab 1-network-tests or lab 2-custom-test you can skip this section except for AVD installation

### Installing AVD

Follow the [instructions](https://avd.arista.com/stable/docs/installation/collection-installation.html) to install AVD:

```bash
pip install "pyavd[ansible]"
ansible-galaxy collection install arista.avd
```

### Starting containerlab

> **Note**
> if you are running in ATD, you can skip this step

- download cEOS in version 4.32.0F

```bash
ardl --token <ARISTA TOKEN> get eos --version 4.32.0F --image-type cEOS --import-docker
```

> **Note**
> You can generate an ARISTA TOKEN with an arista.com account following these steps: TODO

- Start initial topology

```bash
# From the root of the repository
cd containerlab-topology
sudo containerlab deploy --topo topology.yml --reconfigure
cd ..
```

## Run eos_validate_state playbook in check mode

```bash
# from the root of the repo
cd avd
ansible-playbooks playbooks/validate.yml --check
```

4. Analyze the first results

5. Update NRFU tests to with
    - Under test `VerifyBGPIPv4UnicastCount:` update `number: 4`
    - Under test `VerifyLoopbackCount:` update `number: 1`

6. Run ANTA testing

    ```bash
    anta nrfu --catalog 1-network-tests/nrfu.yml table
    ```

## Focusing on Leaf devices

Run testing only on leaf devices

```bash
anta nrfu --catalog 1-network-tests/nrfu.yml --tags leaf table
```

## Run a debug command on a specific device

```bash
anta debug run-cmd -c "show lldp neighbors" --device spine01
```

## Group result per test or per device

```bash
anta nrfu -c 1-network-tests/nrfu.yml table --group-by device
anta nrfu -c 1-network-tests/nrfu.yml table --group-by test
```

## Collect Data from network

1. Edit list of command to capture

    ```bash
    vim 1-network-tests/snapshot.yml
    ```

    You can show commands to capture JSON or Text outputs.

2. Capture commands using ANTA

    ```bash
    anta exec snapshot -c 1-network-tests/snapshot.yml
    ```
