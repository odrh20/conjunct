# Abstract base class for structure of SAPDA configuration, which is either a Leaf or a Tree.
from abc import ABC, abstractmethod


class Structure(ABC):
    def __init__(self, sapda, stack):
        self.sapda = sapda
        self.stack = stack

    def has_empty_stack(self):
        return self.stack == ['e']

    @abstractmethod
    def get_denotation(self):
        pass


# Class for leaf (active) nodes which inherits from the Node class.
# Leaves are active and need to be processed. They are labelled by a triple of (current state, remaining input, stack).

class Leaf(Structure):
    def __init__(self, sapda, stack, current_state, remaining_input):
        super().__init__(sapda, stack)
        self.current_state = current_state
        self.remaining_input = remaining_input

    def get_denotation(self):
        return self.current_state, self.remaining_input, self.stack

    def split_leaf(self, letter, conjuncts):
        if self.stack == 'e':
            print("Error. Trying to split a branch with empty stack.")
            return
        if len(self.stack) == 1:
            internal_stack = ['e']
        else:
            internal_stack = self.stack[1:]

        if letter == 'e':
            child_input = self.remaining_input
        elif len(self.remaining_input) == 1:
            child_input = 'e'
        else:
            child_input = self.remaining_input[1:]

        children = []
        for next_state, push_string in conjuncts:

            children.append(Leaf(self.sapda, push_string, next_state, child_input))

        return Tree(self.sapda, internal_stack, children)

# Class for configuration trees, which consist of an internal node (represented by a stack) and
# at least two children. Children are either trees themselves, or they are leaves.


class Tree(Structure):

    def __init__(self, sapda, stack, children):
        super().__init__(sapda, stack)
        self.children = children  # A list of Leaf and Tree objects

    def get_denotation(self):
        # Returns denotation of the tree, given by a pair of (list of children (Leaf or Tree), root node)
        children_denoted = []
        for child in self.children:
            if isinstance(child, Leaf):
                children_denoted.append(child.get_denotation())
            else:
                children_denoted += child.get_tree_denotation

        return children_denoted, self.stack

    def get_active_branches(self):
        # Get a list of Leaf objects contained in the Tree

        active_branches = []
        for child in self.children:
            if isinstance(child, Leaf):
                active_branches.append(child)
            else:
                active_branches += child.get_active_branches()
        return active_branches



