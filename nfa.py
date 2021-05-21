import copy


class NFA:
    def __init__(self, states, input_alphabet, transitions,
                 initial_state, accepting_states):
        """Instantiate NFA object"""
        self.states = states
        self.input_alphabet = input_alphabet
        self.transitions = transitions
        self.initial_state = initial_state
        self.accepting_states = accepting_states
        #self.current_state = self.initial_state

    def make_config_dict__(self, input_word):
        """
        Make a dictionary with every possible configuration (state, remaining input) which has an available
        transition as keys.
        The value for each key is a pair (next input letter, next state)

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

    def make_config_dict(self, input_word):

        config_dict = dict()
        for state in self.states:
            for i in range(len(input_word)):
                if state in self.transitions and (input_word[i] in self.transitions[state] or 'e' in self.transitions[state]):
                    config_dict[(state, input_word[i:])] = []
                    if input_word[i] in self.transitions[state]:
                        for next_state in self.transitions[state][input_word[i]]:
                            config_dict[(state, input_word[i:])].append((input_word[i], next_state))
                    if 'e' in self.transitions[state]:
                        for next_state in self.transitions[state]['e']:
                            config_dict[(state, input_word[i:])].append(('e', next_state))
            if state in self.transitions and 'e' in self.transitions[state]:
                config_dict[(state, 'e')] = []
                for next_state in self.transitions[state]['e']:
                    config_dict[(state, 'e')].append(('e', next_state))
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

    def run_transitions(self, config, config_dict, computation):
        # return configuration, computation, accept bool, reject bool

        # Check if in an accepting configuration
        if self.is_accepting_config(config):
            return config, computation, True, False

        # Check if in a rejecting configuration
        if config not in config_dict:
            return config, computation, False, True

        # Check if the next transition is non-deterministic
        if len(config_dict[config]) > 1:
            return config, computation, False, False

        # Else, run transition, update the current state, configuration and computation, then recurse.
        letter, state = config_dict[config][0]
        #self.current_state = state
        new_config = self.run_transition(config, letter, state)
        computation.append(new_config)
        return self.run_transitions(new_config, config_dict, computation)


    def run_machine(self, input_string):
        """Run the machine on input string"""
        current_config = self.initial_state, input_string
        computation = [current_config]
        config_dict = self.make_config_dict(input_string)
        current_config, computation, accept, reject = self.run_transitions(current_config, config_dict, computation)

        if accept:
            return "Word accepted!", computation
        if reject:
            return "Word rejected!"

        # Else we reached a deterministic transition. Use backtracking search algorithm.
        return self.search(current_config, config_dict, computation)

    def search(self, config, config_dict, computation, depth=0, path=None):
        # Apply this function at a configuration where a choice of transition is available
        if path is None:
            path = []

        # Iterate through possible transitions at given configuration
        for index, (letter, state) in enumerate(config_dict[config]):

            # Make a copy of inputs, in case we need to backtrack
            _config = copy.deepcopy(config)
            _config_dict = copy.deepcopy(config_dict)
            _computation = copy.deepcopy(computation)

            # In the copy of the dictionary, remove all other transitions from this configuration
            _config_dict[config] = [(letter, state)]
            new_config, new_computation, accept, reject = self.run_transitions(_config, _config_dict, _computation)

            if accept:
                return "Word accepted!", new_computation

            if reject:
                if index + 1 == len(config_dict[config]):
                    if depth == 0:
                        return "Word rejected!"
                    else:
                        # We have guessed and gone wrong. Delete node which led to the dead end and backtrack to previous depth.
                        last_letter, last_state, last_config, last_dict, last_computation = path.pop()
                        last_dict[last_config].remove((last_letter, last_state))
                        return self.search(last_config, last_dict, last_computation, depth - 1, path)

            if not (accept or reject):
                path.append((letter, state, config, config_dict, computation))
                return self.search(new_config, _config_dict, new_computation, depth + 1, path)

# beginning with 'a', ending with 'a', and containing no consecutive 'b's
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

# third symbol from the right must be 0
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

# a DFA for 0*, no 1s allowed
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

# accepts word of the form '01u10'
nfa4 = NFA(
    states={'q0', 'q1', 'q2', 'q3', 'q4'},
    input_alphabet={'0', '1'},
    transitions={
        'q0': {'0': {'q1'}},
        'q1': {'1': {'q2'}},
        'q2': {'0': {'q2'}, '1': {'q2', 'q3'}},
        'q3': {'0': {'q4'}}
    },
    initial_state='q0',
    accepting_states={'q4'}
)

#nfa_dict = nfa.make_config_dict('aa')
#print(nfa_dict)



#nfa3_dict = nfa3.make_config_dict('0110')
#print(nfa3_dict)

#print(nfa3_dict[('q1', '0110')][0][1])



print("")
#print(nfa2.run_machine('01'))

#print(nfa.run_machine('aaabaaaaaabaaaaabaaa'))

#print(nfa2.make_config_dict('0101'))

#print(nfa4.run_machine('01101101'))

while True:
    input_str = input("Enter the input string, or type 'Exit': ")
    if input_str == 'Exit':
        break
    print(nfa4.run_machine(input_str))
