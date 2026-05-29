# Ansible Nokia ISAM FTTN 7330 Collection
This collection is a fork of https://github.com/Qalthos/linkybook.utils which describes the skeleton of a network device collection. It also uses https://github.com/ansible-network/cli_rm_builder to scaffold the ressource module folders and boiler code.

This Ansible Collection contains modules to manage Nokia ISAM FTTN 7330 devices. The Nokia ISAM FTTN Line-up is of the Device Type MSAN. Most of the options available are for different types of OSI Layer 2 protocols. As such it is very different from other Ansible Network Collections whcih are specialised on routers and switches. This repository is under active development and not yet ready for production use! It is not supported by  nor affiliated to Nokia in any way! Use at your own risk!


Currently available modules are:
* cli_command
* cli_config
* isam_interfaces
* isam_bridges
* isam_ethernet_line
* isam_facts
* isam_vlans

Resource module roadmap (TODO):

The detailed live command tree and resource roadmap are documented in:

* `docs/command_tree.md`
* `docs/resource_module_roadmap.md`

First planned config resource branches:

* `isam_pon_interfaces`
* `isam_ethernet_onts`
* `isam_equipment_onts`
* `isam_qos_interfaces`
* `isam_qos_profiles`
* `isam_xdsl_lines`
* `isam_xdsl_profiles`
* `isam_link_agg`
* `isam_xstp`
* `isam_equipment`

Status and management data should generally be added as structured `isam_facts`
resources before introducing dedicated read-only info modules.

## Requirements & Installation
### Requirements
* Ansible 2.15 or higher
* Python 3.10 or higher
* Nokia ISAM FTTN 7330 device running ISAM Release R6.2.04m
 or higher

### Installation
Install the collection from Github:
```
git clone https://github.com/jahknem/nokia.isam.git
cd nokia.isam
pip3 install -r requirements.txt
ansible-galaxy collection build
ansible-galaxy collection install nokia-isam-*.tar.gz
```
### Usage

To use this collection the following needs to be added to the inventory:
```
ansible_connection: ansible.netcommon.network_cli
ansible_network_os: nokia.isam.isam
```
When using `gather_facts: true`, Ansible's default `smart` resolver does not
automatically map `nokia.isam.isam` to this collection's facts module.

Add this to `ansible.cfg`:
```ini
[defaults]
facts_modules = smart, nokia.isam.isam_facts
```

Or set it in inventory/group vars:
```yaml
ansible_facts_modules:
  - smart
  - nokia.isam.isam_facts
```

You can always run facts explicitly as a task:
```yaml
- name: Gather ISAM facts
  nokia.isam.isam_facts:
```

Some modules take a long time to complete due to the slow nature of the device. To increase the timeout for these modules the following can be added to the inventory:
```
ansible_command_timeout : 150
```
150 Seconds should be enough to complete a transmission of the complete configuration. As such it should also be enough for most other commands.

## Development

[This](https://docs.ansible.com/ansible/latest/network/dev_guide/developing_resource_modules_network.html) is a starting point.

Step 1) Create a resource module model
Step 2) Scaffold it with [resource_module_builder](https://github.com/ansible-network/resource_module_builder) or [cli_rm_builder](https://github.com/ansible-network/cli_rm_builder)
