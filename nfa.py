import copy
import time
import random

class NFA:
    def __init__(self, states, input_alphabet, transitions,
                 initial_state, accepting_states):
        """Instantiate NFA object"""
        self.states = states
        self.input_alphabet = input_alphabet
        self.transitions = transitions
        self.initial_state = initial_state
        self.accepting_states = accepting_states
        self.current_state = self.initial_state


    def make_config_dict(self, input_word):
        """
        Make a dictionary with every possible configuration (state, remaining input) which has an available
        transition as keys.
        The value for each key is a dictionary mapping the next input letter to read to possible next states

        """
        config_dict = dict()
        for state in self.states:
            for i in range(len(input_word)):
                if state in self.transitions and (input_word[i] in self.transitions[state] or 'e' in self.transitions[state]):
                    config_dict[(state, input_word[i:])] = dict()
                    if input_word[i] in self.transitions[state]:
                        config_dict[(state, input_word[i:])][input_word[i]] = self.transitions[state][input_word[i]]
                    if 'e' in self.transitions[state]:
                        config_dict[(state, input_word[i:])]['e'] = self.transitions[state]['e']

            if state in self.transitions and 'e' in self.transitions[state]:
                config_dict[(state, 'e')] = dict()
                config_dict[(state, 'e')]['e'] = self.transitions[state]['e']

        return config_dict

    def is_accepting_config(self, config):
        return config[0] in self.accepting_states and config[1] == 'e'

    @staticmethod
    def run_transition(config, letter, next_state):

        if letter == 'e':
            return next_state, config[1]

        if len(config[1]) == 1:
            return next_state, 'e'

        return next_state, config[1][1:]

    def run_deterministic_transitions(self, config, config_dict, local_computation=None):
        # return configuration, local_computation, accept bool, reject bool

        if local_computation is None:
            local_computation = []

        # Check if in an accepting configuration
        if self.is_accepting_config(config):
            return config, local_computation, True, False

        # Check if in a rejecting configuration
        if config not in config_dict:
            return config, local_computation, False, True

        # Check if the next transition is non-deterministic
        if len(config_dict[config]) > 1:
            return config, local_computation, False, False

        for letter in config_dict[config]:
            if len(config_dict[config][letter]) > 1:
                return config, local_computation, False, False

        # Else, run transition, update the current state, configuration and local computation, then recurse.
        (letter, (state,)), = config_dict[config].items()
        self.current_state = state
        new_config = self.run_transition(config, letter, state)
        local_computation.append(new_config)
        return self.run_deterministic_transitions(new_config, config_dict, local_computation)


    def check_if_accept(self):
        """Checks if the current state is one of the accept states."""
        return self.current_state in self.accepting_states


    def run_machine(self, input_string):
        """Run the machine on input string"""
        current_config = self.initial_state, input_string
        computation = [current_config]
        config_dict = self.make_config_dict(input_string)

        current_config, computation, accept, reject = self.run_deterministic_transitions(current_config, config_dict, computation)
        if accept:
            return "Word accepted!", computation
        if reject:
            return "Word rejected!"

        # Else we reached a deterministic transition. Use backtracking search algorithm.
        return self.search(current_config, config_dict, computation)

    def search(self, config, config_dict, computation, depth=0):
        # Apply this function at a configuration where a choice of transition is available

        # Make a copy of inputs
        _config = copy.deepcopy(config)
        _config_dict = copy.deepcopy(config_dict)
        _computation = copy.deepcopy(computation)

        # Choose a transition at random from config dictionary
        letter = random.choice(list(config_dict[config]))
        next_state = random.choice(tuple(config_dict[config][letter]))

        # In the copy of the config dictionary, remove all other transitions from this configuration
        _config_dict[config] = dict()
        _config_dict[config][letter] = {next_state}








        return _config_dict[config], letter, next_state





        # for i in range(len(input_string)):
        #     computation.append((self.current_state, input_string[i:]))
        #     self.get_next_states(input_string[i])
        #
        # if not self.check_if_accept():
        #     return "Input string rejected."
        # else:
        #     computation.append((self.current_state, 'e'))
        #     return "Input string accepted. Computation: ", computation


# NFA which matches strings beginning with 'a', ending with 'a', and containing
# no consecutive 'b's
nfa = NFA(
    states={'q0', 'q1', 'q2'},
    input_alphabet={'a', 'b'},
    transitions={
        'q0': {'a': {'q1'}},
        # Use 'e' as the key name for empty string (epsilon) transitions
        'q1': {'a': {'q1'}, 'e': {'q2'}},
        'q2': {'b': {'q0'}}
    },
    initial_state='q0',
    accepting_states={'q1'}
)

nfa2 = NFA(
    states={'q0', 'q1', 'q2', 'q3'},
    input_alphabet={'0', '1'},
    transitions={
        'q0': {'0': {'q0', 'q1'}, '1': {'q0'}},
        'q1': {'0': {'q2'}, '1': {'q2'}},
        'q2': {'0': {'q3'}, '1': {'q3'}}
    },
    initial_state='q0',
    accepting_states={'q3'}
)

nfa3 = NFA(
    states={'q0', 'q1'},
    input_alphabet={'0', '1'},
    transitions={
        'q0': {'0': {'q0'}, '1': {'q1'}},
        'q1': {'0': {'q1'}, '1': {'q1'}},
    },
    initial_state='q0',
    accepting_states={'q0'}
)

nfa_dict = nfa2.make_config_dict('1110')
print(nfa_dict)



print("")
print(nfa2.run_machine('1110'))

#print(nfa2.make_config_dict('0101'))


