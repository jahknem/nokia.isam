To create a new facts.py file for a resource module, follow these steps:

1. Create a new python file named facts.py in the facts folder of the resource module.

2. Import the necessary modules for the facts class, such as type from __future__, deepcopy from copy, and iteritems from six.

3. Import the Route_mapsArgs class from the argspec folder, and the Route_mapsTemplate class from the rm_templates folder, as shown in the example.

4. Define a new class, Route_mapsFacts, and add the __init__ method to it. This method should take the module and subspec as arguments, and set the argument_spec variable to the argument_spec attribute of the Route_mapsArgs class.

5. Define a get_config method that takes a connection argument and returns the configuration for the route maps on the device using connection.get().

6. Define a populate_facts method that takes a connection, ansible_facts, and data arguments. This method should parse the configuration for route maps using the Route_mapsTemplate class, and populate the ansible_facts dictionary with the parsed data.

7. After implementing these steps, the Route_mapsFacts class should be able to collect and parse the configuration data for route maps, and populate the ansible_facts dictionary with the parsed data.




