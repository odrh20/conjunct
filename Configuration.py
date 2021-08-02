from abc import ABC, abstractmethod
from PrintTree import *


class Configuration(ABC):
    """
    Abstract base class for SAPDA configurations, which are either Leaf or Tree objects.
    """

    def __init__(self, sapda, stack):
        self.sapda = sapda
        self.stack = stack

    def has_empty_stack(self):
        return self.stack == ['e']

    @abstractmethod
    def get_denotation(self):
        pass

    @abstractmethod
    def has_valid_transition(self):
        pass

    @abstractmethod
    def get_active_branches(self):
        pass

    @abstractmethod
    def get_all_leaves(self):
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

    @abstractmethod
    def get_tree_structure(self):
        pass

    def get_stack_string(self):
        string = ""
        for symbol in self.stack:
            string += symbol
        return string

    @abstractmethod
    def print_tree(self):
        pass

    @abstractmethod
    def get_tree_depth(self):
        pass

    @abstractmethod
    def __eq__(self, other):
        pass

    def __ne__(self, other):
        return not self.__eq__(other)


class Leaf(Configuration):
    """
    Class for SAPDA leaves, which are labelled by a triple of (current state, remaining input, stack contents).
    """

    def __init__(self, sapda, stack, state, remaining_input, internal_stack=None, depth=0):
        super().__init__(sapda, stack)
        self.children = None
        self.state = state
        self.remaining_input = remaining_input
        if internal_stack is None:
            self.internal_stack = []
        else:
            self.internal_stack = internal_stack
        self.depth = depth

    def __eq__(self, other):

        if not (isinstance(self, Leaf) and isinstance(other, Leaf)):
            return False
        return (self.sapda == other.sapda) and (self.stack == other.stack) and (self.state == other.state) and \
               (self.remaining_input == other.remaining_input) and (self.internal_stack == other.internal_stack) and \
               (self.depth == other.depth)

    def get_denotation(self):
        """
        The denotation of a Leaf object is a triple of (current state, remaining input, stack)
        """
        return self.state, self.remaining_input, self.stack

    def get_tree_structure(self):
        return Node((self.state, self.remaining_input, self.get_stack_string()))([])

    def get_tree_depth(self):
        return 0

    def get_dict_key(self):
        return self.state, self.remaining_input, tuple(self.stack), tuple(self.internal_stack), self.depth

    def get_active_branches(self):
        if self.has_valid_transition():
            return [self]
        return []

    def get_all_leaves(self):
        return [self]

    def has_valid_transition(self):

        return self.state in self.sapda.transitions and (not self.has_empty_stack()) and \
               self.stack[0] in self.sapda.transitions[self.state] and \
               (self.remaining_input[0] in self.sapda.transitions[self.state][self.stack[0]] or
                'e' in self.sapda.transitions[self.state][self.stack[0]])

    def run_leaf_transition(self, letter, pop_symbol, conjuncts):
        """
        Carry out a given transition on a Leaf.
        If there is more than one conjunct, it is a conjunctive transition and split_leaf will be called to make a Tree.
        """

        if len(conjuncts) > 1:
            return self.split_leaf(letter, conjuncts)

        return_remaining_input = self.remaining_input

        (next_state, push_string), = conjuncts
        if letter == 'e':
            return_state = next_state

        elif len(self.remaining_input) == 1:
            return_state, return_remaining_input = next_state, 'e'

        else:
            return_state, return_remaining_input = next_state, self.remaining_input[1:]

        # Update stack
        return_stack = self.leaf_stack_transition(pop_symbol, push_string)

        return Leaf(self.sapda, return_stack, return_state, return_remaining_input, self.internal_stack, self.depth)

    def leaf_stack_transition(self, pop_symbol, push_string):
        """
        A SAPDA stack is given by a list of stack symbols with the top at the head. For any transition, remove
        pop_symbol from the head and append each symbol from the push_string to the top in reverse order.
        If the push_string is 'e', don't append anything.
        """

        if len(self.stack) == 0:
            print("LEN STACK IS 0")
            return self.stack

        if self.stack[0] != pop_symbol:
            print("FIRST ELEMENT OF STACK NOT POP SYMBOL")
            return self.stack

        # Pop:
        if len(self.stack) == 1:
            return_stack = ['e']
        else:
            return_stack = self.stack[1:]

        # Push:
        if push_string != 'e':
            for symbol in reversed(push_string):
                return_stack.insert(0, symbol)

        if len(return_stack) > 1 and return_stack[-1] == 'e':
            return_stack = return_stack[:-1]

        return return_stack

    def split_leaf(self, letter, conjuncts):
        """
        Split leaf into a tree for conjunctive transitions (assuming there are at least two conjuncts)
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
        for (next_state, push_string) in conjuncts:
            child_stack = []
            for symbol in push_string:
                child_stack.append(symbol)
            children.append(Leaf(self.sapda, child_stack, next_state, child_input, internal_stack, self.depth+1))

        return Tree(self.sapda, internal_stack, children)

    def synchronise(self):
        return self

    def find_leaf_for_transition(self, leaf, letter, conjuncts):
        #print("calling find_leaf_for_transition on Leaf object")

        if leaf not in self.get_active_branches():
            print("WARNING. CALLED find_leaf_for_transition but the leaf is not the right one")
        return self.run_leaf_transition(letter, self.stack[0], conjuncts)

    def print_tree(self):
        return drawTree2(False)(False)(self.get_tree_structure())


# Class for configuration trees, which consist of an internal node (represented by a stack) and
# at least two children. Children are either trees themselves, or they are leaves.

class Tree(Configuration):

    def __init__(self, sapda, stack, children):
        super().__init__(sapda, stack)
        self.children = children  # A list of Leaf and Tree objects
        self.state = None
        self.remaining_input = None

    def __eq__(self, other):
        if not (isinstance(self, Tree) and isinstance(other, Tree)):
            return False
        if len(self.children) != len(other.children):
            return False
        same_check = [self.sapda == other.sapda, self.stack == other.stack]
        for i in range(len(self.children)):
            same_check.append(self.children[i] == other.children[i])

        return all(same_check)

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

        #print("CHILD HAS TRANSITION: ", child_has_transition)
        return any(child_has_transition)

    def get_tree_depth(self):
        depths = []
        for child in self.children:
            depths.append(child.get_tree_depth())
        return 1 + max(depths)

    def get_all_leaves(self):
        leaves = []
        for child in self.children:
            if isinstance(child, Leaf):
                leaves.append(child)
            else:
                leaves += child.get_all_leaves()
        return leaves

    def get_active_branches(self):
        """
        :return: List of Leaf objects contained in the Tree
        """

        active_branches = []
        for leaf in self.get_all_leaves():
            if leaf.has_valid_transition():
                active_branches.append(leaf)
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
        """

        # First check if the children of the current Tree are synchronised. If so, collapse them to a single Leaf.
        if isinstance(self.children[0], Leaf) and self.children[0].has_empty_stack():
            synchronised_leaves = [self.children[0]]
            for child in self.children[1:]:
                if isinstance(child, Leaf) and child.has_empty_stack() and child.remaining_input == \
                        self.children[0].remaining_input and child.state == self.children[0].state:
                    synchronised_leaves.append(child)
            if len(synchronised_leaves) == len(self.children):
                return Leaf(self.sapda, self.stack, self.children[0].state,
                            self.children[0].remaining_input)

        # If the tree's children are not synchronised, recursively call the function on each child.
        return_children = []
        for child in self.children:
            return_children.append(child.synchronise())

        return Tree(self.sapda, self.stack, return_children)

    def find_leaf_for_transition(self, leaf, letter, conjuncts):
        """
        Given a leaf and transition, find a matching leaf in the tree and apply transition to it.
        """

        new_children = self.children
        for i in range(len(new_children)):

            if new_children[i] == leaf:
                new_children[i] = new_children[i].run_leaf_transition(letter, new_children[i].stack[0], conjuncts)
                break

            elif isinstance(new_children[i], Tree):
                new_children[i] = new_children[i].find_leaf_for_transition(leaf, letter, conjuncts)

        return Tree(self.sapda, self.stack, new_children)

    def get_tree_structure(self):
        child_nodes = []
        for child in self.children:
            child_nodes.append(child.get_tree_structure())
        return Node(self.get_stack_string())(child_nodes)

    def print_tree(self):
        return drawTree2(False)(False)(self.get_tree_structure())
