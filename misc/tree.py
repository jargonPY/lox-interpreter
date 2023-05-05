def print_tree(root, indent=0):
    """Recursively print a tree data structure."""
    if root is None:
        return
    print(" " * indent + str(root.value))
    for child in root.children:
        print_tree(child, indent + 2)


class Node:
    def __init__(self, value):
        self.value = value
        self.children = []


"""
In this updated implementation, the add_child() method adds a new child node
to the current node's children list and returns the TreeBuilder instance, allowing
for method chaining. The add_children() method takes a variable number of arguments,
each representing a child node value, and adds them all as child nodes of the current
node.

The go_to_parent() method moves the current node up to its parent node by popping the parent
node from a stack that stores the parent nodes. The go_to_child() method moves the current
node down to one of its child nodes specified by an index. Before moving down, it pushes the
current node onto the parent stack so it can later navigate back up the tree.

In the updated usage example, we create a multi-level tree using the add_children(), go_to_child(),
and go_to_parent() methods to navigate through the tree and add child nodes at different levels. The
resulting tree is stored in the root attribute of the final TreeBuilder instance.
"""


class TreeBuilder:
    def __init__(self, root_value):
        self.root = Node(root_value)
        self.current_node = self.root
        self.parent_stack = []

    def add_child(self, child_value):
        new_child = Node(child_value)
        self.current_node.children.append(new_child)
        return self

    def add_children(self, *children_values):
        for child_value in children_values:
            new_child = Node(child_value)
            self.current_node.children.append(new_child)
        return self

    def go_to_parent(self):
        if self.parent_stack:
            self.current_node = self.parent_stack.pop()
        return self

    def go_to_child(self, child_index):
        child_node = self.current_node.children[child_index]
        self.parent_stack.append(self.current_node)
        self.current_node = child_node
        return self


# Usage example
tree = (
    TreeBuilder("A")
    .add_children("B", "C")
    .go_to_child(0)
    .add_child("D")
    .add_children("E", "F")
    .go_to_parent()
    .go_to_child(1)
    .add_children("G", "H")
    .go_to_child(1)
    .add_child("I")
    .add_child("J")
    .go_to_parent()
    .go_to_parent()
    .add_child("K")
    .root
)

print_tree(tree)
