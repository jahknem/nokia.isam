The rm_templates folder is used to define the NetworkTemplate classes which are used to parse the configuration of network resources. These classes consist of a list of parser definitions and associated functions that facilitate both facts gathering and native command generation for the given network resource.

To create a new resource module template:

1. Create a new file in the rm_templates folder for the new resource module. For example, new_resource.py for a resource module named new_resource.

2. Import the NetworkTemplate class from the ansible_collections.ansible.netcommon.plugins.module_utils.network.common.network_template module.

3. Define a new class that derives from the NetworkTemplate class. For example:

    ```
    class New_resourceTemplate(NetworkTemplate):
        def __init__(self, lines=None, module=None):
            super(New_resourceTemplate, self).__init__(lines=lines, tmplt=self, module=module)
    ```
4. Define a list of parser definitions for the class. Each parser definition is a dictionary with the following keys:
    - name: The name of the parser. This should match the name of the network resource being parsed.
    - getval: A regular expression pattern used to extract values from the configuration.
    - group: The name of the group in the regular expression pattern that matches the value to be extracted.
    - splitval: A regular expression pattern used to split the value into a list of sub-values.
    - setval: A function that takes a parsed value and generates a set of commands to configure the network resource.
5. Define any additional helper functions that are used by the setval functions.

6. Add the list of parser definitions to the class as the PARSERS attribute.

7. Use the new class in the corresponding resource module file (located in the modules folder) to parse and generate configuration for the network resource.