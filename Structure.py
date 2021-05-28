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

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def get_dict_key(self):
        pass

    @abstractmethod
    def has_valid_transition(self):
        pass


# Class for leaf (active) nodes which inherits from the Node class.
# Leaves are active and need to be processed. They are labelled by a triple of (current state, remaining input, stack).

class Leaf(Structure):
    def __init__(self, sapda, stack, current_state, remaining_input):
        super().__init__(sapda, stack)
        self.current_state = current_state
        self.remaining_input = remaining_input

    def get_denotation(self):
        """
        The denotation of a Leaf object is a triple of (current state, remaining input, stack)

        """
        return self.current_state, self.remaining_input, self.stack

    def get_dict_key(self):
        return self.current_state, self.remaining_input, tuple(self.stack)

    def has_valid_transition(self):
        return self.current_state in self.sapda.transitions and self.stack[0] in \
               self.sapda.transitions[self.current_state]

    def __str__(self):
        return f"Leaf (State: {self.current_state}, Input: {self.remaining_input}, Stack: {self.stack})"

    def split_leaf(self, letter, conjuncts):
        """
        :param letter: input letter to be read
        :param conjuncts: tuples of (next state, string to push to stack)
        :return: Tree with child Leaves for each conjunct
        """
        if self.stack == ['e']:
            print("Error. Trying to split a branch with empty stack.")
            return

        if letter != 'e' and letter != self.remaining_input[0]:
            print("Error. Trying to apply transition with wrong next letter.")
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

            children.append(Leaf(self.sapda, [push_string], next_state, child_input))

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
            children_denoted.append(child.get_denotation())

        return children_denoted, self.stack

    def get_dict_key(self):
        children_denoted = []
        for child in self.children:
            children_denoted.append(child.get_dict_key())

        return tuple(children_denoted), tuple(self.stack)

    def has_valid_transition(self):
        child_has_transition = []
        for child in self.children:
            child_has_transition.append(child.has_valid_transition())
        return all(child_has_transition)




    def __str__(self):
        children_message = ""
        for child in self.children:
            children_message += child.__str__()
        return f"Tree\n(Children: {children_message}, \nStack: {self.stack})"

    def get_active_branches(self):
        """
        :return: List of Leaf objects contained in the Tree
        """

        active_branches = []
        for child in self.children:
            if isinstance(child, Leaf):
                active_branches.append(child)
            else:
                active_branches += child.get_active_branches()
        return active_branches

    def collapse_synchronised_leaves(self):
        """
        Checks whether any sibling leaves in the tree are synchronised, and performs one step of collapsing if so.
        Siblings are synchronised if they are all Leaf objects, all have an empty stack, and all have the same
        remaining input and same current state.
        """

        if isinstance(self.children[0], Leaf) and self.children[0].has_empty_stack():
            synchronised_leaves = [self.children[0]]
            for child in self.children[1:]:
                if isinstance(child, Leaf) and child.has_empty_stack() and child.remaining_input == \
                        self.children[0].remaining_input and child.current_state == self.children[0].current_state:
                    synchronised_leaves.append(child)
            if len(synchronised_leaves) == len(self.children):
                return Leaf(self.sapda, self.stack, self.children[0].current_state, self.children[0].remaining_input)

        # If the tree's children are not synchronised, if any of them are Trees then recursively call the function.
        for child in self.children:
            if isinstance(child, Tree):
                child.collapse_synchronised_leaves()

        return self





