# Class representing the entire SAPDA configuration.
# Any configuration is either a single Leaf or a Tree with children that are either Leaf or Tree objects
import copy

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
            self.computation.append(["Configuration: ", new_config.get_denotation()])
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
        If there are any leaves that have no available transitions but have not emptied their stack, there is no path
        to an accepting configuration, so the configuration can be rejected.
        """
        if self.is_accepting_config():
            return False
        if len(self.configuration.get_active_branches()) == 0:
            return True
        for leaf in self.configuration.get_all_leaves():
            if not (leaf.has_valid_transition() or leaf.has_empty_stack()):
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
                if leaf.remaining_input[0] in self.sapda.transitions[leaf.state][leaf.stack[0]]:
                    self.config_dict[leaf.get_dict_key()] = []
                    for transition in self.sapda.transitions[leaf.state][leaf.stack[0]][
                        leaf.remaining_input[0]]:
                        self.config_dict[leaf.get_dict_key()].append((leaf.remaining_input[0], transition))

                # Check for transitions reading 'e'
                if leaf.remaining_input[0] != 'e' and 'e' in self.sapda.transitions[leaf.state][leaf.stack[0]]:
                    if leaf.get_dict_key() not in self.config_dict:
                        self.config_dict[leaf.get_dict_key()] = []
                    for transition in self.sapda.transitions[leaf.state][leaf.stack[0]]['e']:
                        self.config_dict[leaf.get_dict_key()].append(('e', transition))

    def order_active_branches(self):
        """
        Returns list of (leaf, number of available transitions) pairs, ordered by fewest available transitions.
        """
        active_branches = self.configuration.get_active_branches()
        branch_transitions = []
        for branch in active_branches:
            if branch.get_dict_key() not in self.config_dict:
                print("found an active branch that is not in the config_dict. branch: ", branch.get_denotation())
                return False
            else:
                branch_transitions.append([branch, len(self.config_dict[branch.get_dict_key()])])

        branch_transitions.sort(key=lambda x: x[1])
        return branch_transitions

    def is_deterministic_transition(self):
        """
        For the current configuration, check if any active branches have a deterministic transition.
        """
        for leaf in self.configuration.get_active_branches():
            if leaf.get_dict_key() in self.config_dict and len(self.config_dict[leaf.get_dict_key()]) == 1:
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
        #print("curr config: ", self.configuration.get_denotation())
        #print("config dict: ", self.config_dict)
        #print("COMPUTATION: ", self.computation)
        # Check for synchronised leaves. If synchronisation occurs, call this function again.
        if self.configuration.are_synchronised_leaves():
            #print("NEED TO SYNCHRONISE")
            #print("CONFIG BEFORE SYNCH: ", self.configuration.get_denotation())
            new_config = self.configuration.synchronise()
            #print("New CONFIG: ", new_config)
            self.update(new_config)
            #print("CONFIG AFTER SYNCH: ", self.configuration.get_denotation())
            return self.run_deterministic_transitions()

        # Check if in an accepting configuration
        if self.is_accepting_config():
            return True, False

        # Check if in a rejecting configuration
        if self.is_rejecting_config():
            return False, True

        # Check if next transition is non-deterministic:
        if not self.is_deterministic_transition():
            return False, False

        # If the configuration is a single leaf, run the transition:
        if self.is_leaf:
            letter, conjuncts = self.config_dict[self.configuration.get_dict_key()][0]
            new_config = self.configuration.run_leaf_transition(letter, self.configuration.stack[0], conjuncts)
            self.update(new_config)
            return self.run_deterministic_transitions()

        for leaf in self.configuration.get_active_branches():
            if leaf.get_dict_key() in self.config_dict and len(self.config_dict[leaf.get_dict_key()]) == 1 and not leaf.has_empty_stack():
                letter, conjuncts = self.config_dict[leaf.get_dict_key()][0]
                new_config = self.configuration.find_leaf_for_transition(leaf, letter, conjuncts)
                self.update(new_config)
                return self.run_deterministic_transitions()

        print("Couldn't find a leaf within to do transition.")

    def run_machine(self):
        """Run the machine on input string"""

        for letter in self.input_string:
            if self.input_string != 'e' and letter not in self.sapda.input_alphabet:
                return "Word rejected!"

        accept, reject = self.run_deterministic_transitions()

        if accept:
            return "Word accepted!", self.computation
        if reject:
            return "Word rejected!"

        # Else we reached a non-deterministic transition. Use backtracking search algorithm.
        #print("have to use search. current config: ", self.configuration.get_denotation())
        return self.search()

    def search(self, depth=0, path=None):
        if path is None:
            path = []
        #print("DEPTH: ", depth)

        # Iterate through possible transitions at given configuration
        if not self.order_active_branches():
            return "Done"


        for leaf, num_transitions in self.order_active_branches():
            #for branch in self.configuration.get_active_branches():
                #print("active: ", branch.get_denotation())
            #print("current leaf: ", leaf)
            #print("num trans: ", num_transitions)

            for index, (letter, conjuncts) in enumerate(self.config_dict[leaf.get_dict_key()]):
                #print("current leaf: ", leaf.get_dict_key())
                #print("current leaf possible transitions: ", self.config_dict[leaf.get_dict_key()])

                # Make a copy of the SAPDAConfiguration object in case we need to backtrack later
                next_self = copy.deepcopy(self)

                # In the copy of the dictionary, remove all other transitions from this configuration
                #print("old dict: ", next_self.config_dict[leaf.get_dict_key()])
                next_self.config_dict[leaf.get_dict_key()] = [(letter, conjuncts)]
                #print("new dict: ", next_self.config_dict[leaf.get_dict_key()])

                accept, reject = next_self.run_deterministic_transitions()
                #print("accept: ", accept)
                #print("reject: ", reject)

                if accept:
                    return "Word accepted!", next_self.computation

                if reject:

                    if index + 1 == num_transitions:

                        if depth == 0:
                            return "Word rejected!"
                        else:
                            # Need to backtrack
                            #print("Backtracking")
                            last_leaf, tried_letter, tried_conjuncts, last_config, last_computation, last_dict, last_is_leaf = path.pop()
                            #print("current leaf possible transitions in last dict: ", last_dict[leaf.get_dict_key()])

                            last_self = SAPDAConfiguration(self.sapda, self.input_string, last_computation, last_config, last_dict, last_is_leaf)

                            last_self.config_dict[last_leaf.get_dict_key()].remove((tried_letter, tried_conjuncts))
                            #print(f"deleted {tried_letter, tried_conjuncts} from {last_leaf.get_dict_key()}")
                            return last_self.search(depth - 1, path)

                if not (accept or reject):
                    path.append((leaf, letter, conjuncts, self.configuration, self.computation, self.config_dict, self.is_leaf))
                    return next_self.search(depth + 1, path)


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

# a^n b^n c^n (n > 0) : this is a deterministic SAPDA
sapda2 = SAPDA(
    states={'q0', 'qbc+', 'qbc-', 'qac+', 'qac-', 'qb'},
    input_alphabet={'a', 'b', 'c'},
    stack_alphabet={'Z', 'D'},
    transitions={
        'q0': {'Z': {'e': {(('qbc+', 'Z'), ('qac+', 'Z'))}}
               },
        'qbc+': {'Z': {'a': {(('qbc+', 'Z'),)}, 'b': {(('qbc+', 'DZ'),)}},
                 'D': {'b': {(('qbc+', 'DD'),)}, 'c': {(('qbc-', 'e'),)}}
                 },
        'qbc-': {'D': {'c': {(('qbc-', 'e'),)}},
                 'Z': {'e': {(('q0', 'e'),)}}
                 },
        'qac+': {'Z': {'a': {(('qac+', 'DZ'),)}},
                 'D': {'a': {(('qac+', 'DD'),)}, 'b': {(('qb', 'D'),)}}
                 },
        'qb': {'D': {'b': {(('qb', 'D'),)}, 'c': {(('qac-', 'e'),)}},
                 },
        'qac-': {'D': {'c': {(('qac-', 'e'),)}},
                 'Z': {'e': {(('q0', 'e'),)}}
                 },
    },
    initial_state='q0',
    initial_stack_symbol='Z'
)

# {w$uw : w,u ∈ {a,b}∗}
sapda3 = SAPDA(
    states={'q0', 'qw', 'qe', 'qa1', 'qa2', 'qb1', 'qb2'},
    input_alphabet={'a', 'b', '$'},
    stack_alphabet={'Z', '#'},
    transitions={
        'q0': {'Z': {'a': {(('qa1', 'Z'), ('q0', 'Z'))}, 'b': {(('qb1', 'Z'), ('q0', 'Z'))}, '$': {(('qw', 'Z'),)}}
               },
        'qa1': {'Z': {'a': {(('qa1', '#Z'),)}, 'b': {(('qa1', '#Z'),)}, '$': {(('qa2', 'Z'),)}},
                '#': {'a': {(('qa1', '##'),)}, 'b': {(('qa1', '##'),)}, '$': {(('qa2', '#'),)}}
                },
        'qb1': {'Z': {'a': {(('qb1', '#Z'),)}, 'b': {(('qb1', '#Z'),)}, '$': {(('qb2', 'Z'),)}},
                '#': {'a': {(('qb1', '##'),)}, 'b': {(('qb1', '##'),)}, '$': {(('qb2', '#'),)}}
                },
        'qa2': {'Z': {'a': {(('qa2', 'Z'),), (('qe', 'Z'),)}, 'b': {(('qa2', 'Z'),)}},
                '#': {'a': {(('qa2', '#'),), (('qe', '#'),)}, 'b': {(('qa2', '#'),)}}
                },
        'qb2': {'Z': {'a': {(('qb2', 'Z'),)}, 'b': {(('qb2', 'Z'),), (('qe', 'Z'),)}},
                '#': {'a': {(('qb2', '#'),)}, 'b': {(('qb2', '#'),), (('qe', '#'),)}}
                },

        'qw': {'Z': {'a': {(('qw', 'Z'),), (('qe', 'e'),)}, 'b': {(('qw', 'Z'),), (('qe', 'e'),)}}
               },
        'qe': {'Z': {'e': {(('qe', 'e'),)}},
               '#': {'a': {(('qe', 'e'),)}, 'b': {(('qe', 'e'),)}}}
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

#sapda = SAPDAConfiguration(sapda1, 'ca')
sapda = SAPDAConfiguration(sapda3, 'ab$bbbbabbbbab')

print(sapda.run_machine())

print(sapda.computation)
#
#




# leaf1 = Leaf(sapda1, ['e'], 'q0', 'abc')
# leaf2 = Leaf(sapda1, ['Z'], 'q0', 'abc')
# leaf3 = Leaf(sapda1, ['Z'], 'q1', 'abc')
# subtree1 = Tree(sapda1, ['a', 'Z'], [leaf1, leaf1])
# subtree2 = Tree(sapda1, ['a'], [leaf3, subtree1])
# subtree3 = Tree(sapda1, ['e'], [leaf2, subtree2])
# tree1 = Tree(sapda1, ['b', 'Z'], [leaf2, subtree3])

leaf1 = Leaf(sapda3, ['e'], 'qe', 'e')

subtree = Tree(sapda3, ['e'], [leaf1, leaf1])
tree1 = Tree(sapda3, ['e'], [leaf1, subtree])
tree2 = Tree(sapda3, ['e'], [leaf1, tree1])
tree3 = Tree(sapda3, ['e'], [leaf1, tree2])



# print(tree3)
# print(tree3.are_synchronised_leaves())
# tree3 = tree3.synchronise()
# print(tree3)
# print(tree3.are_synchronised_leaves())
# tree3 = tree3.synchronise()
# print(tree3)
# print(tree3.are_synchronised_leaves())
# tree3 = tree3.synchronise()
# print(tree3)
# print(tree3.are_synchronised_leaves())
# tree3 = tree3.synchronise()
# print(tree3)
# print(tree3.are_synchronised_leaves())


