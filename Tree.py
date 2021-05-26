# Class representing the entire tree of a SAPDA configuration.
# Any tree matches one of the following two patterns:
# 1) A single Leaf node
# 2) Sibling Leaf nodes with one Internal parent node (Leaf_1, Leaf_2, ..., Leaf_n)(Internal)

from SAPDA import SAPDA
from Leaf import Leaf
from Internal import Internal


class Tree:
    def __init__(self, sapda, input_string, computation=None, configuration=None, config_dict=None):
        if computation is None:
            computation = []
        if config_dict is None:
            config_dict = dict()

        self.sapda = sapda
        self.input_string = input_string
        self.computation = computation
        self.configuration = configuration
        self.config_dict = config_dict

        if self.configuration is None:
            # Initialising a tree of a single Leaf node
            self.configuration = Leaf(self.sapda, self, self.sapda.initial_stack_symbol, self.sapda.initial_state,
                                      self.input_string)

    def is_accepting_config(self):
        """
        A tree is in an accepting configuration if it consists of a single Leaf node with empty stack and no
        remaining input.
        """
        return isinstance(self.configuration, Leaf) and self.configuration.remaining_input == 'e' and \
               self.configuration.has_empty_stack()

    def process_initial_leaf(self):
        """
        Processes the initial leaf. If no conjunctive transitions are encountered, this will determine whether
        the string is accepted. If a conjunctive transition is encountered, the Tree configuration will change.
        """


# words with equal number of a's, b's and c's
sapda1 = SAPDA(
    states={'q0', 'q1', 'q2'},
    input_alphabet={'a', 'b', 'c'},
    stack_alphabet={'Z', 'a', 'b', 'c'},
    transitions={
        'q0': {'Z': {'e': {(('q1', 'Z'), ('q2', 'Z'))}}
               },
        'q1': {'Z': {'a': {(('q1', 'aZ'),)}, 'b': {(('q1', 'bZ'),)}, 'c': {(('q1', 'Z'),)}, 'e': {(('q0', 'e'),)}},
               'a': {'a': {(('q1', 'aa'),)}, 'b': {(('q1', 'e'),)}, 'c': {(('q1', 'a'),)}},
               'b': {'a': {(('q1', 'e'),)}, 'b': {(('q1', 'bb'),)}, 'c': {(('q1', 'b'),)}},
               },
        'q2': {'Z': {'a': {(('q2', 'Z'),)}, 'b': {(('q2', 'bZ'),)}, 'c': {(('q2', 'cZ'),)}, 'e': {(('q0', 'e'),)}},
               'b': {'a': {(('q2', 'b'),)}, 'b': {(('q2', 'bb'),)}, 'c': {(('q2', 'e'),)}},
               'c': {'a': {(('q2', 'c'),)}, 'b': {(('q2', 'e'),)}, 'c': {(('q2', 'cc'),)}},
               },
    },
    initial_state='q0',
    initial_stack_symbol='Z'
)

# a^n b^n (n>=0) (No conjunctive transitions, this is a PDA)
pda = SAPDA(
    states={'q0', 'q1', 'q2', 'q3'},
    input_alphabet={'a', 'b'},
    stack_alphabet={'Z', 'a'},
    transitions={
        'q0': {'Z': {'a': {(('q1', 'aZ'),)}, 'e': {(('q0', 'e'),)}}
               },
        'q1': {'a': {'a': {(('q1', 'aa'),)}, 'b': {(('q2', 'e'),)}},
               },
        'q2': {'a': {'b': {(('q2', 'e'),)}}, 'Z': {'e': {(('q3', 'e'),)}}
               }
    },
    initial_state='q0',
    initial_stack_symbol='Z'
)


print(pda)

sapda_tree = Tree(pda, 'aabb')

print(sapda_tree.is_accepting_config())

print("Current configuration: ", sapda_tree.configuration)

print(sapda_tree.config_dict)

print(sapda_tree.config_dict[sapda_tree.configuration.get_config_tuple()])

print(sapda_tree.configuration.process_leaf())
