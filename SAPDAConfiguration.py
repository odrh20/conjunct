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
            self.computation.append(["Configuration: ", self.configuration.get_denotation()])

        self.update_config_dict()

    def update(self, new_config):
        """
        Call this function at each step of the computation to update the configuration and append it to the computation
        """
        if self.configuration != new_config:
            self.configuration = new_config
            self.computation.append(["Configuration: ", self.configuration.get_denotation()])
            self.update_config_dict()
            if isinstance(self.configuration, Leaf):
                self.is_leaf = True
            else:
                self.is_leaf = False

    def is_accepting_config(self):
        """
        Accept if the configuration is a single leaf with no remaining input and empty stack.
        """
        return self.is_leaf and self.configuration.remaining_input == 'e' and self.configuration.has_empty_stack()

    def is_rejecting_config(self):
        """
        If any leaf in the current configuration has no valid transition there is no way to reach an accepting
        configuration, so the input string can be rejected.
        """
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

    def is_deterministic_transition(self):
        """
        For the current configuration, check if any active branches have a deterministic transition.
        """
        for leaf in self.configuration.get_active_branches():
            if len(self.config_dict[leaf.get_dict_key()]) == 1:
                return True
        return False

    def run_deterministic_transitions(self):
        """
        From a given SAPDA configuration, runs transitions as long as there is only one available.
        Each transition is either an ordinary transition applied to a leaf, a conjunctive transition which splits a
        leaf into a tree, or collapsing of synchronised sibling leaves.
        After each transition, the new configuration is appended to the computation.
        Returns tuple of (Accept, Reject) booleans. If we reach a non-deterministic transition, both are False.
        """

        # Check if in an accepting configuration
        if self.is_accepting_config():
            return True, False

        # Check if in a rejecting configuration
        if self.is_rejecting_config():
            return False, True

        # Check for synchronised leaves. If synchronisation occurs, call this function again.
        current_config = self.configuration
        self.update(self.configuration.synchronise())
        if not current_config == self.configuration:
            return self.run_deterministic_transitions()

        # Check if next transition is non-deterministic:
        if not self.is_deterministic_transition():
            return False, False

        # If the configuration is a single leaf, run the transition:
        if self.is_leaf:
            letter, conjuncts = self.config_dict[self.configuration.get_dict_key()][0]
            self.update(self.configuration.run_leaf_transition(letter, self.configuration.stack[0], conjuncts))
            return self.run_deterministic_transitions()

        # If tree, find a leaf within that has a single valid transition and a non-empty stack.

        new_config = self.configuration
        for i, child in enumerate(self.configuration.children):
            if isinstance(child, Leaf) and len(self.config_dict[child.get_dict_key()]) == 1 and \
                    not child.has_empty_stack():
                letter, conjuncts = self.config_dict[child.get_dict_key()][0]
                new_config.children[i] = child.run_leaf_transition(letter, child.stack[0], conjuncts)
                self.update(new_config)
                return self.run_deterministic_transitions()


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

config = SAPDAConfiguration(pda, "aabb")
print("initial configuration: ", config.configuration.get_denotation())

print(config.run_deterministic_transitions())

print("new configuration: ", config.configuration.get_denotation())

print(config.config_dict)

print(config.computation)
