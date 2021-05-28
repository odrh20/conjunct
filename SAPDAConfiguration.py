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

        self.update_config_dict()

        if isinstance(self.configuration, Leaf):
            self.is_leaf = True
        else:
            self.is_leaf = False

    def is_accepting_config(self):
        return self.is_leaf and self.configuration.remaining_input == 'e' and self.configuration.has_empty_stack()

    def is_rejecting_config(self):
        for leaf in self.configuration.get_active_branches():
            if leaf.get_dict_key() not in self.config_dict:
                return True
        return False

    def update_config_dict(self):
        """
        Add every Leaf in current configuration to dictionary if it has a valid transition.
        Dictionary keys: SAPDA leaves (denoted as a triple of state, input, stack)
        Dictionary values: List of available transitions, where each transition is a pair (letter to read, conjuncts)
        and conjuncts are pairs of (next state, string to push to stack).
        """
        for leaf in self.configuration.get_active_branches():
            if leaf.get_dict_key() not in self.config_dict and leaf.has_valid_transition():

                # Check for transitions reading the next letter
                if leaf.remaining_input[0] in self.sapda.transitions[leaf.current_state][leaf.stack[0]]:
                    self.config_dict[leaf.get_dict_key()] = []
                    for transition in self.sapda.transitions[leaf.current_state][leaf.stack[0]][
                        leaf.remaining_input[0]]:
                        self.config_dict[leaf.get_dict_key()].append((leaf.remaining_input[0], transition))

            # Check for transitions reading 'e'
            if leaf.remaining_input[0] != 'e' and 'e' in self.sapda.transitions[leaf.current_state][leaf.stack[0]]:
                if leaf.get_dict_key() not in self.config_dict:
                    self.config_dict[leaf.get_dict_key()] = []
                for transition in self.sapda.transitions[leaf.current_state][leaf.stack[0]]['e']:
                    self.config_dict[leaf.get_dict_key()].append(('e', transition))

    def make_step(self, letter, pop_symbol, conjuncts):
        """
        Update the configuration by carrying out a given transition.
        Conjuncts are a tuple of pairs of (next state, push string)
        """
        if len(conjuncts) > 1:
            return 
        for next_state, push_string in conjuncts:
            pass


    # def run_transition(self, letter, next_state, pop_symbol, push_string):
    #
    #     # Update state and read letter
    #     if letter == 'e':
    #         self.current_state = next_state
    #
    #     elif len(self.remaining_input) == 1:
    #         self.current_state, self.remaining_input = next_state, 'e'
    #
    #     else:
    #         self.current_state, self.remaining_input = next_state, self.remaining_input[1:]
    #
    #     # Update stack
    #     self.stack_transition(pop_symbol, push_string)
    #
    #     self.update_config_dict()


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
print(sapda1_config.config_dict)
print(sapda1_config.config_dict[('q0', 'aabbcc', ('Z',))])

for conj in sapda1.transitions['q0']['Z']['e']:
    print(conj)

sapda1_config.configuration.stack = ['a', 'Z']

conjuncts = (('q2', 'b'), ('q1', 'b'))

new_tree = sapda1_config.configuration.split_leaf('e', conjuncts)
print(new_tree.get_denotation())
print(new_tree.has_valid_transition())

synch = new_tree.collapse_synchronised_leaves()[1]
print(synch.get_dict_key())
print(synch.get_active_branches())
