<!--
  ~ Copyright (c) 2024 Arista Networks, Inc.
  ~ Use of this source code is governed by the Apache License 2.0
  ~ that can be found in the LICENSE file.
  -->

# ANTA Hello World

🎯 **Objective:** Discover and run ANTA

## Preparation

### Checking ANTA installation

Make sure the two following commands return correctly

```bash
anta --version
anta --help
```

For every ANTA CLI command you can always run `anta foo --help` to get more information.

### Starting containerlab

> **Note**
> if you are running in ATD, you can skip this step

- download cEOS in version 4.33.0F

```bash
ardl --token <ARISTA_TOKEN> get eos --version 4.33.0F --image-type cEOS --import-docker
```

> **Note**
> The ARISTA_TOKEN value comes from your arista.com account profile

- Start the containerlab topology

```bash
# From the root of the repository
cd containerlab
sudo containerlab deploy
```

## Network Ready for Use

1. Review ANTA environment variables that will be set in [`anta.env`](../anta.env)

    ```bash
    # From the root of the repository
    cat anta.env
    ```

2. Load anta parameters

    ```bash
    source anta.env
    ```

3. Run ANTA testing

    ```bash
    anta nrfu --catalog 1-hello-world/catalog.yml
    ```

    To see only the failures:

    ```bash
    anta nrfu --catalog 1-hello-world/catalog.yml --hide success
    ```

4. Analyze the first results

    There should be test failures on `spine1` and `spine2` devices.

5. Update the [`catalog.yml`](1-hello-world/catalog.yml) file:
    - Under test [`VerifyBGPPeerCount`](https://anta.arista.com/stable/api/tests.routing.bgp/#anta.tests.routing.bgp.VerifyBGPPeerCount) update the expected number of peers (`num_peers`) of the `evpn` address family to **`2`** for the `spines` devices
    - Under test [`VerifyLoopbackCount`](https://anta.arista.com/stable/api/tests.interfaces/#anta.tests.interfaces.VerifyLoopbackCount) update the expected number of loopbacks to **`1`** for the `spines` devices

6. Run ANTA again, there should be no failures now

    ```bash
    anta nrfu --catalog 1-hello-world/catalog.yml
    ```

### Focusing on Leaf devices

Run testing only on leaf devices

```bash
anta nrfu --catalog 1-hello-world/catalog.yml --tags leaf
```

## Collect a batch of command outputs from the devices

1. Review the list of command to collect

    ```bash
    cat 1-hello-world/snapshot.yml
    ```

    Commands can be collected in JSON or TEXT format.

2. Collect commands using ANTA

    ```bash
    anta exec snapshot -c 1-hello-world/snapshot.yml
    ```

## Next steps

ANTA CLI [documentation](https://anta.arista.com/stable/cli/overview/)
