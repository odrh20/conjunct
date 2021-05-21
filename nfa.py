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

    def get_next_states(self, input_letter):
        """
        Returns a list of pairs (input_letter, next_state) for all next states that can be reached by reading a
        given input letter, and of pairs ('e', next_state) for all next states that can be reached by reading the
        empty word.
        """
        next_states = []

        if input_letter in self.transitions[self.current_state]:
            for next_state in self.transitions[self.current_state][input_letter]:
                next_states.append((input_letter, next_state))

        if 'e' in self.transitions[self.current_state]:
            for next_state in self.transitions[self.current_state][input_letter]:
                next_states.append(('e', next_state))

        return next_states

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



    def check_if_accept(self):
        """Checks if the current state is one of the accept states."""
        return self.current_state in self.accepting_states

    def run_machine(self, input_string):
        """Run the machine on input string"""
        computation = []
        for i in range(len(input_string)):
            computation.append((self.current_state, input_string[i:]))
            self.get_next_states(input_string[i])

        if not self.check_if_accept():
            return "Input string rejected."
        else:
            computation.append((self.current_state, 'e'))
            return "Input string accepted. Computation: ", computation


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


print(nfa2.make_config_dict('0101'))
