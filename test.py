from textwrap import dedent

data = dedent("""configure ethernet
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
echo "ethernet"
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
line 1/1/8/1
  port-type uni
  admin-up
  mau 1
    type 1000basebx10d
    power up
  exit
exit
line 1/1/8/2
  port-type uni
  admin-up
  mau 1
    type 1000basebx10d
    power up
  exit
exit
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
""")

from copy import deepcopy
from operator import contains
from anytree import Node, PreOrderIter, RenderTree
import debugpy

from ansible.module_utils.six import iteritems



# Counts the number of spaces at the beginning of a string
def _count_spaces(line):
    spaces = 0
    for char in line:
        if char == ' ':
            spaces += 1
        else:
            break
    return spaces

# Parses the config into a tree structure and cleans up the config so that only relevant data is returned
# The tree structure is determined by the number of spaces at the beginning of each line
def _parse_config_to_tree( config):
    if not config:
        return None
    chapter = 0
    last_spaces = 0
    root = None
    parent_node = None
    for line in config.splitlines():

        # Check if line is valid
        if line.startswith('echo') or line.startswith('#'):
            continue

        # Only here the actual content begins
        # Check if parent node exists. Otherwise create it using first line
        if parent_node is None:
            root = Node(line.split('#',1)[0].strip())
            parent_node = root
            prev_node = root
            
        # The "exit" string is not relevant for us but we need to keep track of the indentation. If the indent is smaller than the previous line, we need to go up the tree
        elif "exit" in line:
            if _count_spaces(line) < last_spaces:
                parent_node = parent_node.parent   
            else: 
                continue

        # Check if line is a child of the previous line as a greater indent means the line has to be a child of the previous line
        elif _count_spaces(line) > last_spaces:
            parent_node = prev_node
            prev_node = Node(line.split('#',1)[0].strip(), parent=prev_node)


        
        # In all other cases the current line is a sibling of the previous line
        else:
            prev_node = Node(line.split('#',1)[0].strip(), parent=parent_node)
        
        # In any case, the indentation spaces of the current line become the last spaces to be used for the next line
        last_spaces = _count_spaces(line)
        print(RenderTree(root))
    return root


def _flatten_config(config):
    if not config:
        return None
    flat_config = []
    root = _parse_config_to_tree(config)
    for leave in root.leaves:
        line = []
        for node in leave.path:
            line.append(node.name)
        flat_config.append(" ".join(line))
    return flat_config

out = _flatten_config( data)
print(out)
