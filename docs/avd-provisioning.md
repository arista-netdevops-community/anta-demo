<!--
  ~ Copyright (c) 2024 Arista Networks, Inc.
  ~ Use of this source code is governed by the Apache License 2.0
  ~ that can be found in the LICENSE file.
  -->

# Configure EOS for testing

## Configuration Management

### Inventory

- Inventory file: [atd-inventory/inventory.yml](../atd-inventory/inventory.yml)
- AVD variables: [atd-inventory/group_vars](../atd-inventory/group_vars)

### Commands

- Build and deploy

```bash
ansible-playbook playbooks/atd-fabric-deploy.yml
```

- Build only

```bash
ansible-playbook playbooks/atd-fabric-deploy.yml --tags build
```

- Build & deploy via eAPI

```bash
ansible-playbook playbooks/atd-fabric-deploy.yml --tags deploy_eapi
```
