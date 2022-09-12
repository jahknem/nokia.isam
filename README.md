# Ansible Nokia ISAM FTTN 7330 Collection
This collection is a fork of https://github.com/Qalthos/linkybook.utils which describes the skeleton of a network device collection. It also uses https://github.com/ansible-network/cli_rm_builder to scaffold the ressource module folders and boiler code.

This Ansible Collection contains modules to manage Nokia ISAM FTTN 7330 devices. The Nokia ISAM FTTN Line-up is of the Device Type MSAN. Most of the options available are for different types of OSI Layer 2 protocols. As such it is very different from other Ansible Network Collections whcih are specialised on routers and switches. This repository is under active development and not yet ready for production use! It is not supported by  nor affiliated to Nokia in any way! Use at your own risk!


Currently available modules are:
* cli_command
* cli_config
* isam_interfaces

Future modules will include:
* isam_bridges
* isam_ethernet_ont
* isam_facts
* isam_ont_interfaces
* isam_ont_slots
* isam_ping
* isam_qos_interfaces
* isam_vlans

## Requirements & Installation
### Requirements
* Ansible 2.9 or higher
* Python 3.6 or higher
* Nokia ISAM FTTN 7330 device running ISAM Release R6.2.04m
 or higher

### Installation
Install the collection from Github:
```
git clone https://github.com/jahknem/nokia.isam.git
cd nokia.isam
pip3 install -r requirements.txt
ansible-galaxy collection build
ansible-galaxy collection install isam-isam-*.tar.gz
```
### Usage

To use this collection the following needs to be added to the inventory:
```
ansible_connection: ansible.netcommon.network_cli
ansible_network_os: isam.isam.isam
```
Some modules take a long tiome to complete due to the slow nature of the device. To increase the timeout for these modules the following can be added to the inventory:
```
ansible_command_timeout : 150
```
150 Seconds should be enough to complete a transmission of the complete configuration. As such it should also be enough for most other commands.