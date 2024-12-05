<!--
  ~ Copyright (c) 2024 Arista Networks, Inc.
  ~ Use of this source code is governed by the Apache License 2.0
  ~ that can be found in the LICENSE file.
  -->

# ANTA in AVD

## Overview

This lab takes you through the following steps:

1. Using `eos_validate_state` role in AVD in check mode to observe what test catalogs are generated.
2. Running `eos_validate_state` towards the lab.
3. Using a custom ANTA catalog in `eos_validate_state`

> **Reminder**
>
> This lab has been built with AVD 5.1.0 and ANTA v1.1.0

## Preparation

> **Note**
>
> if you have just finished lab 1-network-tests or lab 2-custom-test you can skip this section except for AVD installation

### Installing AVD

Follow the [instructions](https://avd.arista.com/stable/docs/installation/collection-installation.html) to install AVD:

```bash
pip install "pyavd[ansible]==5.1.0"
ansible-galaxy collection install "arista.avd==5.1.0"
```

### Starting containerlab

> **Note**
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
ansible_httpapi_host: '{{ ansible_host }}'
ansible_connection: httpapi
ansible_httpapi_use_ssl: true
# Certs _should_ be validate when outside of lab environment
ansible_httpapi_validate_certs: false
ansible_network_os: eos
ansible_httpapi_port: 443
# May not be needed
ansible_become: true
ansible_become_method: enable
```

## Run `eos_validate_state` in check mode

In this section, the goal is to run the `eos_validate_state` in check mode, which will execute the equivalent of an `anta nrfu --dry-run`.

> **IMPORTANT**
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

Take a look
