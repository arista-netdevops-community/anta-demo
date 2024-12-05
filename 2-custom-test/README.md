<!--
  ~ Copyright (c) 2024 Arista Networks, Inc.
  ~ Use of this source code is governed by the Apache License 2.0
  ~ that can be found in the LICENSE file.
  -->

# Building an ANTA test

🎯 **Objective:** Writing and executing a custom ANTA test

> 📃 **Note**
>
> Refer to the [ANTA Documentation](https://anta.arista.com/stable/advanced_usages/custom-tests/) on developing an ANTA test for more details.

A custom Python package is provided in this lab under the `custom` folder.

In this lab, we are going to create a test (`VerifyVlanStatus`) in a separate Python package.
The Python package is accessible in the Python envirnement using the `PYTHONPATH` definition in [anta.env](../anta.env).

The `VerifyVlanStatus` test verifies if specified VLANs are active using the output of the `show vlan` command.

## The `AntaTest` subclass definition

A test is a Python class where a test function is defined and will be run by the framework.

ANTA provides an abstract class [AntaTest](https://anta.arista.com/stable/api/models/#test-definition). This class does the heavy lifting and provide the logic to define, collect and test data.

### Docstring and Class Variables

````python
from typing import ClassVar
from anta.models import AntaTest, AntaCommand, AntaTemplate


class VerifyVlanStatus(AntaTest):
    """Verifies if the VLANs provided as input are active.

    Expected Results
    ----------------
    * Success: The test will pass if all specified VLANs are active.
    * Failure: The test will fail if at least one specified VLAN is not active.

    Examples
    --------
    ```yaml
    custom.vlan:
      - VerifyVlanStatus:
    ```
    """

    categories: ClassVar[list[str]] = ["vlan"]
    commands: ClassVar[list[AntaCommand | AntaTemplate]] = [AntaCommand(command="show vlan", revision=1)]

    @AntaTest.anta_test
    def test(self) -> None:
        pass
````

The `AntaTest` class from which all ANTA tests inherit defines some mandatory class Variables.

- `name` [Optional starting ANTA v1.2.0]: Name of the test - use the Class name if not provided.
- `description` [Optional starting ANTA 1.2.0]: A human readable description of your test - use the first line of the docstring if not provided.
- `categories`: a list of categories to sort test. The existing categories are listed on ANTA website.
- `commands`: a list of `AntaCommand` and/or `AntaTemplate` to run for this test to be able to execute the `test` function.

> 📃 **Note**
>
> If you do not intend to contribute back your test to ANTA main repository, you do not need to respect the docstring format.
> If the docstring is not defined, the `description` class variable must be defined.

### The `Input` class definition

[`AntaTest.Input`](https://anta.arista.com/stable/api/models/#anta.models.AntaTest.Input) is a [pydantic model](https://docs.pydantic.dev/latest/concepts/models/) that allow test developers to define their test inputs. `pydantic` provides out of the box error handling for test input validation based on the type hints defined by the test developer.

To develop an ANTA test with inputs, it is necessary to define the pydantic model for them, this will define the YAML structure of the test inputs in the catalog.

For `VerifyVlanStatus`, the model defines one input called `vlans` that is the list of VLAN ID to verify.
`pydantic` allows to validate the inputs by defining constraints. We are using the type `anta.custom_types.Vlan` that defines an integer between 0 and 4094: `Vlan = Annotated[int, Field(ge=0, le=4094)]`.

````python
from typing import ClassVar
from anta.models import AntaTest, AntaCommand, AntaTemplate
from anta.custom_types import Vlan


class VerifyVlanStatus(AntaTest):
    """Verifies if the VLANs provided as input are active.

    Expected Results
    ----------------
    * Success: The test will pass if all specified VLANs are active.
    * Failure: The test will fail if at least one specified VLAN is not active.

    Examples
    --------
    ```yaml
    custom.vlan:
      - VerifyVlanStatus:
    ```
    """

    categories: ClassVar[list[str]] = ["vlan"]
    commands: ClassVar[list[AntaCommand | AntaTemplate]] = [AntaCommand(command="show vlan", revision=1)]

    class Input(AntaTest.Input):
        """Input model for the VerifyVlanStatus test."""

        vlans: list[Vlan]
        """The VLAN IDs to verify."""

    @AntaTest.anta_test
    def test(self) -> None:
        pass
````

### The `test` function definition

The next step is to define the `test` function, it is the function that parse the output of the command(s) collected and decide if the test is a success, a failure or if the test should be skipped.

The complexity of the `test` function may differ depending on how much parsing and checking you need to do to validate the output of the command(s).

The first step would be to get a device and inspect the structure of the output of the command `show vlan`:

``` bash
$ anta debug run-cmd -d leaf1 -c "show vlan"
Run command show vlan on leaf1
{
    'vlans': {
        '1': {'name': 'default', 'dynamic': False, 'status': 'active', 'interfaces': {'Ethernet6': {'privatePromoted': False, 'blocked': None}, 'PeerEthernet6': {'privatePromoted': False, 'blocked': None}, 'Port-Channel1': {'privatePromoted': False, 'blocked': None}}},
        '110': {'name': 'Tenant_A_OP_Zone_1', 'dynamic': False, 'status': 'active', 'interfaces': {'Cpu': {'privatePromoted': False, 'blocked': None}, 'Port-Channel1': {'privatePromoted': False, 'blocked': None}, 'Port-Channel4': {'privatePromoted': False, 'blocked': None}, 'Vxlan1': {'privatePromoted': False, 'blocked': None}}},
        '160': {'name': 'Tenant_A_VMOTION', 'dynamic': False, 'status': 'active', 'interfaces': {'Port-Channel1': {'privatePromoted': False, 'blocked': None}, 'Vxlan1': {'privatePromoted': False, 'blocked': None}}},
        '1199': {'name': 'VLAN1199', 'dynamic': True, 'status': 'active', 'interfaces': {'Cpu': {'privatePromoted': False, 'blocked': None}, 'Port-Channel1': {'privatePromoted': False, 'blocked': None}, 'Vxlan1': {'privatePromoted': False, 'blocked': None}}},
        '3009': {'name': 'MLAG_L3_VRF_Tenant_A_OP_Zone', 'dynamic': False, 'status': 'active', 'interfaces': {'Cpu': {'privatePromoted': False, 'blocked': None}, 'Port-Channel1': {'privatePromoted': False, 'blocked': None}}},
        '4093': {'name': 'MLAG_L3', 'dynamic': False, 'status': 'active', 'interfaces': {'Cpu': {'privatePromoted': False, 'blocked': None}, 'Port-Channel1': {'privatePromoted': False, 'blocked': None}}},
        '4094': {'name': 'MLAG', 'dynamic': False, 'status': 'active', 'interfaces': {'Cpu': {'privatePromoted': False, 'blocked': None}, 'Port-Channel1': {'privatePromoted': False, 'blocked': None}}}
    },
    'sourceDetail': ''
}
```

> 📃 **Note**
>
> The above `anta debug` command is equivalent to use `show vlan | json` in EOS CLI.

````python
from typing import ClassVar
from anta.models import AntaTest, AntaCommand, AntaTemplate
from anta.custom_types import Vlan


class VerifyVlanStatus(AntaTest):
    """Verifies if the VLANs provided as input are active.

    Expected Results
    ----------------
    * Success: The test will pass if all specified VLANs are active.
    * Failure: The test will fail if at least one specified VLAN is not active.

    Examples
    --------
    ```yaml
    custom.vlan:
      - VerifyVlanStatus:
    ```
    """

    categories: ClassVar[list[str]] = ["vlan"]
    commands: ClassVar[list[AntaCommand | AntaTemplate]] = [AntaCommand(command="show vlan", revision=1)]

    class Input(AntaTest.Input):
        """Input model for the VerifyVlanStatus test."""

        vlans: list[Vlan]
        """The VLAN IDs to verify."""

    @AntaTest.anta_test
    def test(self) -> None:
        """Main test function for VerifyVlanStatus."""
        command_output = self.instance_commands[0].json_output
        self.inputs: VerifyVlanStatus.Input

        self.result.is_success()
        for vlan in self.inputs.vlans:
            if str(vlan) not in command_output["vlans"]:
                self.result.is_failure(f"VLAN {vlan} is not configured.")
                continue
            if not command_output["vlans"][str(vlan)]["status"] == "active":
                self.result.is_failure(f"VLAN {vlan} is not active.")
````

That's it the test is created!

## Create the catalog

The custom Python package is `custom` and the test class `VerifyVlanStatus` is defined in the `custom.vlan` Python module.
The test catalog will look like:

```yaml
custom.vlan:
  - VerifyVlanStatus:
      vlans:
        - 110
        - 160
```

## Run the test from the ANTA CLI

```bash
# From the root of the repository
$ source anta.env
$ anta nrfu -c 2-custom-test/catalog.yml

                                                               All tests results
┏━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ Device ┃ Test Name        ┃ Test Status ┃ Message(s)                  ┃ Test description                                    ┃ Test category ┃
┡━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ spine1 │ VerifyVlanStatus │ failure     │ VLAN 110 is not configured. │ Verifies if the VLANs provided as input are active. │ VLAN          │
│        │                  │             │ VLAN 160 is not configured. │                                                     │               │
├────────┼──────────────────┼─────────────┼─────────────────────────────┼─────────────────────────────────────────────────────┼───────────────┤
│ spine2 │ VerifyVlanStatus │ failure     │ VLAN 110 is not configured. │ Verifies if the VLANs provided as input are active. │ VLAN          │
│        │                  │             │ VLAN 160 is not configured. │                                                     │               │
├────────┼──────────────────┼─────────────┼─────────────────────────────┼─────────────────────────────────────────────────────┼───────────────┤
│ leaf1  │ VerifyVlanStatus │ success     │                             │ Verifies if the VLANs provided as input are active. │ VLAN          │
├────────┼──────────────────┼─────────────┼─────────────────────────────┼─────────────────────────────────────────────────────┼───────────────┤
│ leaf2  │ VerifyVlanStatus │ success     │                             │ Verifies if the VLANs provided as input are active. │ VLAN          │
├────────┼──────────────────┼─────────────┼─────────────────────────────┼─────────────────────────────────────────────────────┼───────────────┤
│ leaf3  │ VerifyVlanStatus │ success     │                             │ Verifies if the VLANs provided as input are active. │ VLAN          │
├────────┼──────────────────┼─────────────┼─────────────────────────────┼─────────────────────────────────────────────────────┼───────────────┤
│ leaf4  │ VerifyVlanStatus │ success     │                             │ Verifies if the VLANs provided as input are active. │ VLAN          │
└────────┴──────────────────┴─────────────┴─────────────────────────────┴─────────────────────────────────────────────────────┴───────────────┘
```

You can play with the Inputs further
