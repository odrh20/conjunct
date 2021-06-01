# Abstract base class for structure of SAPDA configuration, which is either a Leaf or a Tree.
import copy
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
    def has_valid_transition(self):
        pass

    @abstractmethod
    def get_active_branches(self):
        pass

    @abstractmethod
    def synchronise(self):
        pass

    @abstractmethod
    def run_leaf_transition(self, letter, pop_symbol, conjuncts):
        pass

    @abstractmethod
    def find_leaf_for_transition(self, leaf, letter, conjuncts):
        pass





# Class for leaf (active) nodes which inherits from the Node class.
# Leaves are active and need to be processed. They are labelled by a triple of (current state, remaining input, stack).

class Leaf(Structure):
    def __init__(self, sapda, stack, state, remaining_input):
        super().__init__(sapda, stack)
        self.children = None
        self.state = state
        self.remaining_input = remaining_input

    def get_denotation(self):
        """
        The denotation of a Leaf object is a triple of (current state, remaining input, stack)

        """
        return self.state, self.remaining_input, self.stack

    def get_dict_key(self):
        return self.state, self.remaining_input, tuple(self.stack)

    def get_active_branches(self):
        if self.has_valid_transition():
            return [self]
        return []

    def has_valid_transition(self):
        return self.state in self.sapda.transitions and (not self.has_empty_stack()) and \
               self.stack[0] in self.sapda.transitions[self.state]

    def __str__(self):
        return f"Leaf (State: {self.state}, Input: {self.remaining_input}, Stack: {self.stack})"

    def run_leaf_transition(self, letter, pop_symbol, conjuncts):
        """
        Carry out a given transition on a Leaf.
        If there is more than one conjunct, it is a conjunctive transition and split_leaf will be called to make a Tree.
        """
        self_ = copy.copy(self)
        if len(conjuncts) > 1:
            return self_.split_leaf(letter, conjuncts)

        (next_state, push_string), = conjuncts
        if letter == 'e':
            self_.state = next_state

        elif len(self_.remaining_input) == 1:
            self_.state, self_.remaining_input = next_state, 'e'

        else:
            self_.state, self_.remaining_input = next_state, self_.remaining_input[1:]

        # Update stack
        self_ = self_.leaf_stack_transition(pop_symbol, push_string)

        return self_

    def leaf_stack_transition(self, pop_symbol, push_string):
        # A PDA stack is given by a list of stack symbols with the top at the head. For any transition, remove
        # pop_symbol from the head and append each symbol from the push_string to the top in reverse order.
        # If the push_string is 'e', don't append anything.

        self_ = copy.copy(self)

        if len(self_.stack) == 0:
            return self_

        if self_.stack[0] != pop_symbol:
            return self_

        # Pop:
        if len(self_.stack) == 1:
            self_.stack = ['e']
        else:
            self_.stack = self_.stack[1:]

        # Push:
        if push_string != 'e':
            for symbol in reversed(push_string):
                self_.stack.insert(0, symbol)

        if len(self_.stack) > 1 and self_.stack[-1] == 'e':
            self_.stack = self_.stack[:-1]

        return self_

    def split_leaf(self, letter, conjuncts):
        """
        Split leaf into a tree for conjunctive transitions (assuming there are at least two conjuncts)
        :param letter: input letter to be read
        :param conjuncts: tuples of (next state, string to push to stack)
        :return: Tree with child Leaves for each conjunct
        """
        self_ = copy.copy(self)


        if self_.stack == ['e']:
            print("Error. Trying to split a branch with empty stack.")
            return

        if letter != 'e' and letter != self_.remaining_input[0]:
            print("Error. Trying to apply transition with wrong next letter.")
            return

        if len(self_.stack) == 1:
            internal_stack = ['e']
        else:
            internal_stack = self_.stack[1:]

        if letter == 'e':
            child_input = self_.remaining_input
        elif len(self_.remaining_input) == 1:
            child_input = 'e'
        else:
            child_input = self_.remaining_input[1:]

        children = []

        for (next_state, push_string) in conjuncts:
            children.append(Leaf(self_.sapda, [push_string], next_state, child_input))

        return Tree(self_.sapda, internal_stack, children)

    def synchronise(self):
        return self

    def find_leaf_for_transition(self, leaf, letter, conjuncts):
        return self


# Class for configuration trees, which consist of an internal node (represented by a stack) and
# at least two children. Children are either trees themselves, or they are leaves.

class Tree(Structure):

    def __init__(self, sapda, stack, children):
        super().__init__(sapda, stack)
        self.children = children  # A list of Leaf and Tree objects
        self.state = None
        self.remaining_input = None

    def get_denotation(self):
        # Returns denotation of the tree, given by a pair of (list of children (Leaf or Tree), root node)
        children_denoted = []
        for child in self.children:
            children_denoted.append(child.get_denotation())

        return children_denoted, self.stack

    def has_valid_transition(self):
        child_has_transition = []
        for child in self.children:
            child_has_transition.append(child.has_valid_transition())
        return any(child_has_transition)

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
            if isinstance(child, Leaf) and child.has_valid_transition():
                active_branches.append(child)
            elif isinstance(child, Tree):
                active_branches += child.get_active_branches()
        return active_branches

    def run_leaf_transition(self, letter, pop_symbol, conjuncts):
        """
        For a given transition, find a leaf in the tree that only has this transition available and return the new
        tree with this transition applied
        """
        return self

    def synchronise(self):

        """
        Checks whether any sibling leaves in the tree are synchronised, and collapses them to make a Leaf.
        Siblings are synchronised if they are all Leaf objects, all have an empty stack, and all have the same
        remaining input and same current state.
        This function will only synchronise a single group of sibling leaves
        Returns
        """
        self_ = copy.copy(self)

        if isinstance(self.children[0], Leaf) and self.children[0].has_empty_stack():
            synchronised_leaves = [self.children[0]]
            for child in self.children[1:]:
                if isinstance(child, Leaf) and child.has_empty_stack() and child.remaining_input == \
                        self.children[0].remaining_input and child.state == self.children[0].state:
                    synchronised_leaves.append(child)
            if len(synchronised_leaves) == len(self.children):
                return Leaf(self.sapda, self.stack, self.children[0].state,
                            self.children[0].remaining_input)

        # If the tree's children are not synchronised, if any children are Trees then recursively call the function.
        for i in range(len(self.children)):
            if isinstance(self.children[i], Tree):
                old_tree = self.children[i]
                self.children[i] = self.children[i].synchronise()
                if self.children[i] != old_tree:
                    return self

        return self

    def find_leaf_for_transition(self, leaf, letter, conjuncts):
        """
        Given a leaf and transition, finds a leaf in the current tree and carries out transition on this leaf
        """
        self_ = copy.copy(self)
        for i, child in enumerate(self_.children):
            if child == leaf:
                self_.children[i] = child.run_leaf_transition(letter, child.stack[0], conjuncts)

            if isinstance(child, Tree):
                child.find_leaf_for_transition(leaf, letter, conjuncts)

        return self_
