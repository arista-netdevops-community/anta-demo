# Copyright (c) 2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.

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