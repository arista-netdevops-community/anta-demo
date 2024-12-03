<!--
  ~ Copyright (c) 2024 Arista Networks, Inc.
  ~ Use of this source code is governed by the Apache License 2.0
  ~ that can be found in the LICENSE file.
  -->

# Building an ANTA test step by step

## Overview

This lab shows how to make a custom test available to ANTA by installing a
Python package that contains it, making it importable by Python.

## Preparation

> **Note**
> if you have just finished lab 1-network-tests you can skip this section

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

## Steps

A custom library is provided part of this repository under `custom` folder. All your tests should be created here in this demo context.

In this demo, we are going to recreate an existing tests (`VerifyUptime`) in our own library using [`custom/example.py`](./custom/example.py) file.

## Python imports

### Mandatory imports

The following elements have to be imported to write a test:

- [anta.models.AntaTest](https://www.anta.ninja/v0.7.2/api/models/#anta.models.AntaTest): class that gives you all the tooling for your test
- [anta.models.AntaCommand](https://www.anta.ninja/v0.7.2/api/models/#anta.models.AntaCommand): A class to abstract an Arista EOS command

```python
from anta.models import AntaTest, AntaCommand
```

### ANTA Test creation

A test is a python class where a test function is defined and will be run by the framework. ANTA provides an abstract class AntaTest. This class does the heavy lifting
and provide the logic to define, collect and test data.

First you need to declare your class and then define your test function.

#### Class Skeleton

Let's add the class skeleton by adding the docstring

> **Note**
> If you don't intend to contribute back your test to ANTA main repository, you don't need to follow the docstring format
> but it helps to get all the required information about your test documented

````python
from anta.models import AntaTest, AntaCommand

class VerifyUptime(AntaTest):
    """
    This test verifies if the device uptime is higher than the provided minimum uptime value.

    Expected Results
    ----------------
      * success: The test will pass if the device uptime is higher than the provided value.
      * failure: The test will fail if the device uptime is lower than the provided value.
      * skipped: The test will be skipped if the provided uptime value is invalid or negative.

    Examples
    --------
    ```yaml
    custom.example:
      - VerifyUptime:
          minimum: 42
    ```
    """
    ...

    @AntaTest.anta_test
    def test(self) -> None:
        pass
````

#### Metadata information

The `AntaTest` class from which all ANTA tests inherit defines some mandatory Class Variables.

##### Mandatory AntaTest Class Variables

- `name` [Optional starting ANTA v1.2.0]: Name of the test - use the Class name if not provided.
- `description` [Optional starting ANTA 1.2.0]: A human readable description of your test - use the first line of the docstring if not provided.
- `categories`: a list of categories to sort test. The existing categories are listed on ANTA website.
- `commands`: a list of `AntaCommand` and/or `AntaTemplate` to run for this test to be able to execute the `test` function.

````python
# Added for Python3.9 support
from __future__ import annotations

import logging
from typing import Any

from anta.models import AntaTest, AntaCommand

class VerifyUptime(AntaTest):
    """
    This test verifies if the device uptime is higher than the provided minimum uptime value.

    Expected Results
    ----------------
      * success: The test will pass if the device uptime is higher than the provided value.
      * failure: The test will fail if the device uptime is lower than the provided value.
      * skipped: The test will be skipped if the provided uptime value is invalid or negative.

    Examples
    --------
    ```yaml
    custom.example:
      - VerifyUptime:
          minimum: 42
    ```
    """

    name = "VerifyUptime"
    # name = "CustomVerifyUptime"  # TODO: uncomment this if you want to change the test name
                                   # note that it requires a change in the catalog.
    description = "My Custom Test."
    categories = ["custom_system"]
    commands = [AntaCommand(command="show uptime", revision=1)]

    @AntaTest.anta_test
    def test(self) -> None:
        pass
````

#### `Inputs` definition

AntaTest.Input is a [pydantic model](https://docs.pydantic.dev/latest/concepts/models/) that allow test developers to define their test inputs. pydantic provides out of the box error handling for test input validation based on the type hints defined by the test developer.

To develop an ANTA test with inputs, it is sufficient to define the pydantic model for them, this will define the YAML structure of the test inputs in the catalog. This example shows a pretty simple example but you can browse ANTA source code on Github to find more intricate examples (e.g. connectivity tests).

For `VerifyUptime`, the model defines one input interge `minimum` that is used to compare to the return of the show command. Notice the import of `PositiveInteger` added towards the top of the file.

````python
# Added for Python3.9 support
from __future__ import annotations

import logging
from typing import Any

from anta.custom_types import PositiveInteger
from anta.models import AntaTest, AntaCommand

class VerifyUptime(AntaTest):
    """
    This test verifies if the device uptime is higher than the provided minimum uptime value.

    Expected Results
    ----------------
      * success: The test will pass if the device uptime is higher than the provided value.
      * failure: The test will fail if the device uptime is lower than the provided value.
      * skipped: The test will be skipped if the provided uptime value is invalid or negative.

    Examples
    --------
    ```yaml
    custom.example:
      - VerifyUptime:
          minimum: 42
    ```
    """

    name = "VerifyUptime"
    # name = "CustomVerifyUptime"  # TODO: uncomment this if you want to change the test name
                                   # note that it requires a change in the catalog.
    description = "My Custom Test."
    categories = ["custom_system"]
    commands = [AntaCommand(command="show uptime", revision=1)]

    class Input(AntaTest.Input):
        """Input model for the VerifyUptime test."""

        minimum: PositiveInteger
        """Minimum uptime in seconds."""

    @AntaTest.anta_test
    def test(self) -> None:
        pass
````

#### `test` function definition

The next step is to define the `test` function, it is the function that will parse the output of the commands ran and the inputs and decide if the test is a success, a failure or any other state.

The complexity of the `test` function may differ depending on how much parsing and checking you need to do to validate the output of the show command(s).

````python
# Added for Python3.9 support
from __future__ import annotations

import logging
from typing import Any

from anta.custom_types import PositiveInteger
from anta.models import AntaTest, AntaCommand

class VerifyUptime(AntaTest):
    """
    This test verifies if the device uptime is higher than the provided minimum uptime value.

    Expected Results
    ----------------
      * success: The test will pass if the device uptime is higher than the provided value.
      * failure: The test will fail if the device uptime is lower than the provided value.
      * skipped: The test will be skipped if the provided uptime value is invalid or negative.

    Examples
    --------
    ```yaml
    custom.example:
      - VerifyUptime:
          minimum: 42
    ```
    """

    name = "VerifyUptime"
    # name = "CustomVerifyUptime"  # TODO: uncomment this if you want to change the test name
                                   # note that it requires a change in the catalog.
    description = "My Custom Test."
    categories = ["custom_system"]
    commands = [AntaCommand(command="show uptime", revision=1)]

    class Input(AntaTest.Input):
        """Input model for the VerifyUptime test."""

        minimum: PositiveInteger
        """Minimum uptime in seconds."""

    @AntaTest.anta_test
    def test(self) -> None:
        """Main test function for VerifyUptime."""
        command_output = self.instance_commands[0].json_output
        if command_output["upTime"] > self.inputs.minimum:
            self.result.is_success()
        else:
            self.result.is_failure(f"Device uptime is {command_output['upTime']} seconds")
````

> **Note**
> To know how to parse the JSON it is possible to run a debug command against one device from ANTA to retrieve the output:
> TODO: insert

That's it the test is created!

### Install the library

```bash
# from the 2-custom-test directory
pip install .
```

Verify the installation:

```
pip freeze | grep custom
python -c "from custom.example import VerifyUptime"
```

### Create your catalog

Our custom library is `custom` and the test is configured in `custom.example`, the test catalog would look like:

```yaml
custom.example:
  - VerifyUptime:
      minimum: 1
```

### Run your NRFU tests with the CLI

```bash
# From the root of the repository
$ source anta.env
Creating default anta variables
Build auto-complete for anta

$ anta nrfu -c 2-custom-module/nrfu_custom.yml table
╭────────────────────── Settings ──────────────────────╮
│ - ANTA Inventory contains 6 devices (AsyncEOSDevice) │
│ - Tests catalog contains 1 tests                     │
╰──────────────────────────────────────────────────────╯

[23:20:04] INFO     Preparing ANTA NRFU Run ...                                                                            tools.py:294
           INFO     Connecting to devices ...                                                                              tools.py:294
           INFO     Connecting to devices completed in: 0:00:00.194.                                                       tools.py:302
           INFO     Preparing the tests ...                                                                                tools.py:294
           INFO     Preparing the tests completed in: 0:00:00.005.                                                         tools.py:302
           INFO     --- ANTA NRFU Run Information ---                                                                     runner.py:270
                    Number of devices: 6 (6 established)
                    Total number of selected tests: 6
                    Maximum number of open file descriptors for the current ANTA process: 16384
                    ---------------------------------
           INFO     Preparing ANTA NRFU Run completed in: 0:00:00.222.                                                     tools.py:302
           INFO     Running ANTA tests ...                                                                                 tools.py:294
[23:20:05] INFO     Running ANTA tests completed in: 0:00:00.170.                                                          tools.py:302
           INFO     Cache statistics for 'spine01': 0 hits / 1 command(s) (0.00%)                                          runner.py:75
           INFO     Cache statistics for 'spine02': 0 hits / 1 command(s) (0.00%)                                          runner.py:75
           INFO     Cache statistics for 'leaf01': 0 hits / 1 command(s) (0.00%)                                           runner.py:75
           INFO     Cache statistics for 'leaf02': 0 hits / 1 command(s) (0.00%)                                           runner.py:75
           INFO     Cache statistics for 'leaf03': 0 hits / 1 command(s) (0.00%)                                           runner.py:75
           INFO     Cache statistics for 'leaf04': 0 hits / 1 command(s) (0.00%)                                           runner.py:75
  • Running NRFU Tests...100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 6/6 • 0:00:00 • 0:00:00

                                   All tests results
┏━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ Device  ┃ Test Name    ┃ Test Status ┃ Message(s) ┃ Test description ┃ Test category ┃
┡━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ spine01 │ VerifyUptime │ success     │            │ My Custom Test.  │ Custom_System │
├─────────┼──────────────┼─────────────┼────────────┼──────────────────┼───────────────┤
│ spine02 │ VerifyUptime │ success     │            │ My Custom Test.  │ Custom_System │
├─────────┼──────────────┼─────────────┼────────────┼──────────────────┼───────────────┤
│ leaf01  │ VerifyUptime │ success     │            │ My Custom Test.  │ Custom_System │
├─────────┼──────────────┼─────────────┼────────────┼──────────────────┼───────────────┤
│ leaf02  │ VerifyUptime │ success     │            │ My Custom Test.  │ Custom_System │
├─────────┼──────────────┼─────────────┼────────────┼──────────────────┼───────────────┤
│ leaf03  │ VerifyUptime │ success     │            │ My Custom Test.  │ Custom_System │
├─────────┼──────────────┼─────────────┼────────────┼──────────────────┼───────────────┤
│ leaf04  │ VerifyUptime │ success     │            │ My Custom Test.  │ Custom_System │
└─────────┴──────────────┴─────────────┴────────────┴──────────────────┴───────────────┘
```

You can play with the Input.minimum uptime.

## What next ?

You can find more information on [ANTA website](https://anta.arista.com) about how to [build your custom tests](https://anta.arista.com/stable/advanced_usages/custom-tests/)
