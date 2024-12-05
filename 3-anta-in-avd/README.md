<!--
  ~ Copyright (c) 2024 Arista Networks, Inc.
  ~ Use of this source code is governed by the Apache License 2.0
  ~ that can be found in the LICENSE file.
  -->

# ANTA in AVD

## Overview

🎯 **Objective:** Leverage ANTA in AVD `eos_validate_state`

This lab takes you through the following steps:

1. Using `eos_validate_state` role in AVD in check mode to observe what test catalogs are generated.
2. Running `eos_validate_state` towards the lab.
3. Using a custom ANTA catalog in `eos_validate_state`

> ⏳ **Reminder**
>
> This lab has been built with AVD 5.1.0 and ANTA v1.1.0

You can read more about AVD `eos_validate_state` at the following URL: [https://avd.arista.com/5.1/roles/eos_validate_state/](https://avd.arista.com/5.1/roles/eos_validate_state/)

## Preparation

> 📃 **Note**
>
> if you have just finished lab 1-hello-world or lab 2-custom-test you can skip this section except for AVD installation

### Installing AVD

Follow the [instructions](https://avd.arista.com/stable/docs/installation/collection-installation.html) to install AVD:

```bash
pip install "pyavd[ansible]==5.1.0"
ansible-galaxy collection install "arista.avd==5.1.0"
```

### Starting containerlab

> 📃 **Note**
>
> if you are running in ATD, you can skip this step

Refer to lab 1 [Preparation](../1-network-tests/#Preparation) steps.

## The `validate.yml` playbook

The playbook located in `avd/playbooks/validate.yml` imports AVD `eos_validate_state` role is configured to save the ANTA catalogs generated from the structured_configs by AVD.

```yaml
---
- name: Validate states on EOS devices
  hosts: LAB
  gather_facts: false

  tasks:
    - name: validate states on EOS devices
      ansible.builtin.import_role:
        name: arista.avd.eos_validate_state
      vars:
        save_catalog: true
```

To be able to run the playbook against the devices, they must be configured with eAPI enabled over HTTPS and the Ansible variables for each device must contain the following snippet (or equivalent):

```yaml
---
ansible_user: admin
ansible_become: true
ansible_become_method: enable
ansible_connection: ansible.netcommon.httpapi
ansible_network_os: arista.eos.eos
ansible_httpapi_use_ssl: true
# Certs _should_ be validated when outside of lab environment
ansible_httpapi_validate_certs: false
ansible_httpapi_use_proxy: false
```

In this repository, they are defined in the AVD `inventory.yml`

## Run `eos_validate_state` in check mode

In this section, the goal is to run the `eos_validate_state` in check mode, which will execute the equivalent of an `anta nrfu --dry-run`.

> ⚠️ **IMPORTANT**
>
> This step **does not** run any test or command towards the network.

```bash
# from the root of the repo
cd avd
ansible-playbooks playbooks/validate.yml --check
```

This will create several files:

1. Some reports as CSV and Markdown as well as a JSON file per device.

    ```bash
    user@hostname$ tree reports
    reports
    ├── FABRIC-state.csv
    ├── FABRIC-state.md
    └── test_results
        ├── leaf1-results.json
        ├── leaf2-results.json
        ├── leaf3-results.json
        ├── leaf4-results.json
        ├── spine1-results.json
        └── spine2-results.json

    1 directory, 8 files
    ```

    The test report is showing all the tests as `NOT RUN` but allows to see what would have been run without `--check`.

2. One catalog per device showing all the tests that would be run (this is enabled by the `save_catalog: true` in the playbook)

    ```bash
    user@hostname$ tree intended/test_catalogs
    intended/test_catalogs
    ├── leaf1-catalog.yml
    ├── leaf2-catalog.yml
    ├── leaf3-catalog.yml
    ├── leaf4-catalog.yml
    ├── spine1-catalog.yml
    └── spine2-catalog.yml

    0 directories, 6 files
    ```

## Run `eos_validate_state`

In this section, the goal is to run the `eos_validate_state` without check mode so the tests will be executed against the network.

```bash
# from the root of the repo
cd avd
ansible-playbooks playbooks/validate.yml
```

Take a look at the Markdown report, the number of tests executed should have changed.

### Creating a failure to see it in the report

1. Connected to leaf1 and shutdown loopback1

    ```bash
    leaf1#conf
    leaf1(config)#interface Loopback1
    leaf1(config-if-Lo1)#shutdown
    ```

2. re-run the validate playbook

    ```bash
    # from the root of the repo
    cd avd
    ansible-playbooks playbooks/validate.yml
    ```

    Open the report again and notice that some tests are now failing for leaf1 (Loopback1 and Vxlan interfaces are down).

3. Clean up the changes and re-run the validate playbook to restore the state.

### Skipping a test

AVD allows to skip tests, either by name or by categories. More information can be found in the [documentation](https://avd.arista.com/5.x/roles/eos_validate_state/index.html).

For this example we are going to skip the `AvdTestInterfacesState` category.

1. Check the number of test in the "Interfaces" category in the report. (At the time of writing it read 70, new tests are being added and it is topology dependent so this number may not be up-to-date, what matters is that it is non-zero).

2. Update the validate playbook by uncommenting the following lines:

    ```yaml
    ---
    - name: Validate states on EOS devices
      hosts: LAB
      gather_facts: false

      tasks:
        - name: validate states on EOS devices
          ansible.builtin.import_role:
            name: arista.avd.eos_validate_state
          vars:
            save_catalog: true
            # Uncomment the following lines when indicated in the lab  guide
            skip_tests:
              - category: AvdTestInterfacesState
    ```

3. Run the playbook again.

    The Interfaces category should be gone from the report and the total number of tests should have decreased.

    > **📃 Note**
    >
    > If you want to skip specific interfaces only you can refer to the `eos_designs` AVD documentation to see how to set the `validate_state` key under each interface.

It is possible to skip specific tests in a given category as described in the `eos_validate_state` documentation.

> **💡 TIP**
>
> If you feel like some additional tests could be added in `eos_validate_state` open a [Github issue](https://github.com/aristanetworks/avd/issues). The main coverage is on DC designs for now.

## Using a custom catalog

It is possible to leverage custom ANTA catalogs in AVD `eos_validate_state` for example to add built-in ANTA tests which could be missing or even to run your own.

This section will take you through using the test built in lab 2 (a duplicate of `VerifyUptime`) in a custom catalog in AVD.

> 📃 **Note**
>
> If you have not run lab2. you can still run this lab, skip step 1.

1. Make sure the `custom` python package is installed and available.

    ```bash
    user@hostname$ pip freeze | grep custom
    # Example output if installed as editable install:
    # custom @ file:///<SOME PATH>>/anta-demo/2-custom-test
    ```

2. The custom catalogs has been built in `3-anta-in-avd/custom_anta_catalogs`.

    ```bash
    user@hostname$ tree 3-anta-in-avd/custom_anta_catalogs
    3-anta-in-avd/custom_anta_catalogs
    ├── LAB.yml
    └── leaf1.yml
    ```

    There are two custom catalogs one applied to all the devices in the `LAB` group in Ansible inventory. (6 devices, 2 spines, 4 leafs). and one applied to only `leaf1`. The name of the file is used by `eos_validate_state` to map a catalog file to a device.

    The two catalogs are as follow:

    The `LAB.yml` catalog has an option to

    ```yaml
    ---
    # 3-anta-in-avd/custom_anta_catalogs/LAB.yml
    # This catalog is applied to all devices in the LAB group in the AVD inventory

    # Use the next test if you have completed lab 2, otherwise comment it.
    custom.example:
      - VerifyUptime:
          minimum: 42

    # If you have not completed lab 2 you can use the built-in ANTA test instead.
    # anta.tests.system:
    #  - VerifyUptime:
    #      minimum: 42
    ```

    The `leaf1.yml` catalog just add a test to validate the default SSL profile. This is only for the purpose of showing how to add a test per device.

    ```yaml
        ---
    # avd/custom_anta_catalogs/leaf1.yml
    # This catalog is applied to only leaf1

    # Using a built-in ANTA test to verify validity of default Arista profile
    anta.tests.security:
    - VerifyAPIHttpsSSL:
        profile: ARISTA_DEFAULT_PROFILE
    ```

3. Edit the `validate.yml` playbook.

    Uncomment the `custom_anta_catalogs_dir: ../3-anta-in-avd/custom_anta_catalogs` line

4. Run the `validate.yml` playbook

    ```bash
    # from the root of the repo
    cd avd
    ansible-playbooks playbooks/validate.yml
    ```

5. Check that in the `intended/test_catalogs` new tests have appeared at the end of the catalogs (notice how leaf1 has the SSL test)

6. Check the makrdown report and see the new category appear (if using the custom test from lab2 you should be seeing a `Custom_System` category)

You can now leverage this lab to create and add your own tests in your own custom catalogs to your `eos_validate_state` role.

## Reference

- ANTA documentation: [https://anta.arista.com](https://anta.arista.com)
- AVD `eos_validate_state`: [https://avd.arista.com/5.1/roles/eos_validate_state/](https://avd.arista.com/5.1/roles/eos_validate_state/)
