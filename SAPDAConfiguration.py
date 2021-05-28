# Class representing the entire SAPDA configuration.
# Any configuration is either a single Leaf or a Tree with children that are either Leaf or Tree objects

from SAPDA import SAPDA
from Structure import *


class SAPDAConfiguration:

    def __init__(self, sapda, input_string, computation=None, configuration=None, config_dict=None,
                 is_leaf=True):
        if computation is None:
            computation = []
        if config_dict is None:
            config_dict = dict()
        self.sapda = sapda
        self.input_string = input_string
        self.computation = computation
        self.configuration = configuration
        self.config_dict = config_dict
        self.is_leaf = is_leaf

        if configuration is None:
            # Initialise a single Leaf node
            self.configuration = Leaf(self.sapda, [self.sapda.initial_stack_symbol], self.sapda.initial_state,
                                      self.input_string)

        if isinstance(self.configuration, Leaf):
            self.is_leaf = True
        else:
            self.is_leaf = False

    def is_accepting_config(self):
        return self.is_leaf and self.configuration.remaining_input == 'e' and self.configuration.has_empty_stack()

    def update_config_dict(self):
        """
        Adds current configuration to dictionary if it has a valid transition for each Leaf within it.
        Dictionary keys: SAPDA configuration (either a single Leaf or a Tree)
        Dictionary values: List of available transitions, where each transition is a pair (letter to read, conjuncts)
        and conjuncts are pairs of (next state, string to push to stack).
        """

        if self.configuration.get_dict_key() not in self.config_dict and self.configuration.has_valid_transition():

        #     # Check for transitions reading the next letter
        #     if self.remaining_input[0] in self.pda.transitions[self.current_state][self.current_stack[0]]:
        #         self.config_dict[self.get_config_tuple()] = []
        #         for next_state, push_stack in self.pda.transitions[self.current_state][self.current_stack[0]][
        #             self.remaining_input[0]]:
        #             self.config_dict[self.get_config_tuple()].append((self.remaining_input[0], push_stack, next_state))
        #
        #     # Check for transitions reading 'e'
        #     if self.remaining_input[0] != 'e' and 'e' in self.pda.transitions[self.current_state][
        #         self.current_stack[0]]:
        #         if self.get_config_tuple() not in self.config_dict:
        #             self.config_dict[self.get_config_tuple()] = []
        #         for next_state, push_stack in self.pda.transitions[self.current_state][self.current_stack[0]]['e']:
        #             self.config_dict[self.get_config_tuple()].append(('e', push_stack, next_state))
        pass



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

sapda1_config = SAPDAConfiguration(sapda1, "aabbcc")
print(sapda1_config.configuration.get_denotation())
print(sapda1_config.configuration.has_valid_transition())


sapda1_config.configuration.stack = ['a', 'Z']


conjuncts = (('q2', 'b'), ('q1', 'b'))

new_tree = sapda1_config.configuration.split_leaf('e', conjuncts)
print(new_tree.get_denotation())
print(new_tree.has_valid_transition())


synch = new_tree.collapse_synchronised_leaves()
print(synch.get_dict_key())



