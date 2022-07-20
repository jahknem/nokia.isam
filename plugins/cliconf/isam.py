#
# (c) 2022 Red Hat Inc.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#

from __future__ import absolute_import, division, print_function


__metaclass__ = type

DOCUMENTATION = """
author: Ansible Networking Team
cliconf: isam
short_description: Example bare minimum cliconf plugin
description:
- This is a cliconf plugin that implements the bare minimum necessary for a new
  device to be supported by the cli_command plugin. Notably this does not do
  anything for cli_config support.
version_added: 0.0.0
"""

import json
import defusedxml.ElementTree as ET
import debugpy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import to_list
from ansible.plugins.cliconf import CliconfBase
from ansible_collections.isam.isam.plugins.cliconf.utils.utils import  getFirstXMLElementText, getXMLElements, removeAlarms, removeCtrlChars



class Cliconf(CliconfBase):
    # These two methods will need to be implemented to support cli_config,
    # which is going to be fairly specific to your device.
    def get_config(self, source='running', flags=None, format=None):
        """Retrieves the specified configuration from the device

        This method will retrieve the configuration specified by source and
        return it to the caller as a string.  Subsequent calls to this method
        will retrieve a new configuration from the device

        :param source: The configuration source to return from the device.
            This argument accepts either `running` or `startup` as valid values.

        :param flags: For devices that support configuration filtering, this
            keyword argument is used to filter the returned configuration.
            The use of this keyword argument is device dependent adn will be
            silently ignored on devices that do not support it.

        :param format: For devices that support fetching different configuration
            format, this keyword argument is used to specify the format in which
            configuration is to be retrieved.

        :return: The device configuration as specified by the source argument.
        """
        if source not in ("running"):
            raise ValueError(
                "fetching configuration from {source} is not supported" % source,
            )
        if format not in ("hierachical", "flat", "xml"):
            raise ValueError(
                "format {format} is not supported" % format,
            )
        if not flags:
            flags = []
        cmd = "info configure"
        cmd += " ".join(to_list(flags))
        return self.send_command(cmd)
        

        raise NotImplementedError

    def edit_config(self, candidate=None, commit=True, replace=None, diff=False, comment=None):
        """Loads the candidate configuration into the network device

        This method will load the specified candidate config into the device
        and merge with the current configuration unless replace is set to
        True.  If the device does not support config replace an errors
        is returned.

        :param candidate: The configuration to load into the device and merge
            with the current running configuration

        :param commit: Boolean value that indicates if the device candidate
            configuration should be  pushed in the running configuration or discarded.

        :param replace: If the value is True/False it indicates if running configuration should be completely
                        replace by candidate configuration. If can also take configuration file path as value,
                        the file in this case should be present on the remote host in the mentioned path as a
                        prerequisite.
        :param comment: Commit comment provided it is supported by remote host
        :return: Returns a json string with contains configuration applied on remote host, the returned
                 response on executing configuration commands and platform relevant data.
               {
                   "diff": "",
                   "response": [],
                   "request": []
               }

        """

        raise NotImplementedError

    def get(self, command=None, prompt=None, answer=None, sendonly=False, newline=True, output=None, check_all=False):
        """Execute specified command on remote device
        This method will retrieve the specified data and
        return it to the caller as a string.
        :param command: command in string format to be executed on remote device
        :param prompt: the expected prompt generated by executing command, this can
                       be a string or a list of strings
        :param answer: the string to respond to the prompt with
        :param sendonly: bool to disable waiting for response, default is false
        :param newline: bool to indicate if newline should be added at end of answer or not
        :param output: For devices that support fetching command output in different
                       format, this keyword argument is used to specify the output in which
                        response is to be retrieved.
        :param check_all: Bool value to indicate if all the values in prompt sequence should be matched or any one of
                          given prompt.
        :return: The output from the device after executing the command
        """ 
        debugpy.listen(3000)
        debugpy.wait_for_client()
        debugpy.breakpoint()
        return self.send_command(
            command=command,
            prompt=prompt,
            answer=answer,
            sendonly=sendonly,
            newline=newline,
            check_all=check_all,
        )

    def get_isam_rpc(self):
        return ['get_config',
                'edit_config',
                'get_capabilities',
                'get',
            ]

    def get_device_info(self):
        """
            'device_info': {
            'network_os': <str>,
            'network_os_version': <str>,
            'network_os_model': <str>,
            'network_os_hostname': <str>,
            'network_os_image': <str>,
            'network_os_platform': <str>,
        },"""
        def get_version(sys_info_xml):
            return getFirstXMLElementText(ET.fromstring(sys_info_xml),"info", "isam-release")

        device_info = dict()
        device_info['network_os'] = 'isam'
        device_info['network_os_platform'] = 'Nokia 7330'

        sys_info_xml = self.get("info configure system xml")
        software_xml = self.get("show software-mngt version etsi detail xml")
        serial_number_xml = self.get("show equipment slot nt-a detail xml")

        device_info['network_os_version'] = get_version(sys_info_xml)

        return super().get_device_info()

    def get_device_operations(self):
        return {
            "supports_diff_replace": False,
            "supports_commit": False,
            "supports_rollback": False,
            "supports_defaults": False,
            "supports_onbox_diff": False,
            "supports_commit_comment": False,
            "supports_multiline_delimiter": False,
            "supports_diff_match": False,
            "supports_diff_ignore_lines": False,
            "supports_generate_diff": False,
            "supports_replace": False,
        }

    def get_option_values(self):
        return {
            "format": ["text"],
            "diff_match": ["line", "strict", "exact", "none"],
            "diff_replace": ["line", "block"],
            "output": [],
        }

    def get_capabilities(self):
        """Returns the basic capabilities of the network device
        This method will provide some basic facts about the device and
        what capabilities it has to modify the configuration.  The minimum
        return from this method takes the following format.
        eg:
            {

                'rpc': [list of supported rpcs],
                'network_api': <str>,            # the name of the transport
                'device_info': {
                    'network_os': <str>,
                    'network_os_version': <str>,
                    'network_os_model': <str>,
                    'network_os_hostname': <str>,
                    'network_os_image': <str>,
                    'network_os_platform': <str>,
                },
                'device_operations': {
                    'supports_diff_replace': <bool>,       # identify if config should be merged or replaced is supported
                    'supports_commit': <bool>,             # identify if commit is supported by device or not
                    'supports_rollback': <bool>,           # identify if rollback is supported or not
                    'supports_defaults': <bool>,           # identify if fetching running config with default is supported
                    'supports_commit_comment': <bool>,     # identify if adding comment to commit is supported of not
                    'supports_onbox_diff: <bool>,          # identify if on box diff capability is supported or not
                    'supports_generate_diff: <bool>,       # identify if diff capability is supported within plugin
                    'supports_multiline_delimiter: <bool>, # identify if multiline demiliter is supported within config
                    'supports_diff_match: <bool>,          # identify if match is supported
                    'supports_diff_ignore_lines: <bool>,   # identify if ignore line in diff is supported
                    'supports_config_replace': <bool>,     # identify if running config replace with candidate config is supported
                    'supports_admin': <bool>,              # identify if admin configure mode is supported or not
                    'supports_commit_label': <bool>,       # identify if commit label is supported or not
                }
                'format': [list of supported configuration format],
                'diff_match': [list of supported match values],
                'diff_replace': [list of supported replace values],
                'output': [list of supported command output format]
            }
        :return: capability as json string
        """

        result = {
            'rpc': self.get_isam_rpc(),
            'network_api': 'cliconf',
            'device_info': self.get_device_info(),
            'device_operations': self.get_device_operations(),
            'format': ["flat", "text"],
            'diff_match': [],
            'diff_replace': [],
            'output': ["flat", "hierarchical","xml"],
        }
        return json.dumps(result)
