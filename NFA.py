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

        self.check_empty_loops = True
        while self.check_empty_loops:
            self.check_empty_loops = self.is_empty_loop()

    def is_empty_loop(self):

        for first_state in self.transitions:
            for letter in self.transitions[first_state]:
                if letter == 'e':
                    for next_state in self.transitions[first_state][letter]:
                        if next_state == first_state:
                            self.transitions[first_state][letter].remove(next_state)
                            if len(self.transitions[first_state][letter]) == 0:
                                del self.transitions[first_state][letter]
                            if not bool(self.transitions[first_state]):
                                del self.transitions[first_state]
                            return True
        return False

    def is_path_to_accept_state(self):

        if len(self.accepting_states) == 0:
            return False

        if self.initial_state in self.accepting_states:
            return True

        for state in self.transitions:
            for letter in self.transitions[state]:
                if len(self.accepting_states.intersection(self.transitions[state][letter])) > 0:
                    return True

        return False

    def __str__(self):
        return f"States: {self.states} \nInput Alphabet: {self.input_alphabet} \nTransitions: {self.transitions} \
               \nInitial State: {self.initial_state} \nAccepting States: {self.accepting_states}"


class NFAConfiguration:
    def __init__(self, nfa, input_string, current_state=None, remaining_input=None, computation=None, config_dict=None):
        if current_state is None:
            current_state = nfa.initial_state
        if computation is None:
            computation = []
        if remaining_input is None:
            remaining_input = input_string
        if config_dict is None:
            config_dict = dict()

        self.nfa = nfa
        self.input_string = input_string
        self.current_state = current_state
        self.remaining_input = remaining_input
        self.computation = computation
        self.config_dict = config_dict
        self.update_config_dict()

    def get_config(self):
        return self.current_state, self.remaining_input

    def update_config_dict(self):
        # Only need to update if the configuration is not already in the dictionary and it has an available transition
        if self.get_config() not in self.config_dict and (self.current_state in self.nfa.transitions):

            # Check for transitions reading the next letter
            if self.remaining_input[0] in self.nfa.transitions[self.current_state]:
                self.config_dict[self.get_config()] = []
                for next_state in self.nfa.transitions[self.current_state][self.remaining_input[0]]:
                    self.config_dict[self.get_config()].append((self.remaining_input[0], next_state))

            # Check for transitions reading 'e'
            if self.remaining_input[0] != 'e' and 'e' in self.nfa.transitions[self.current_state]:
                if self.get_config() not in self.config_dict:
                    self.config_dict[self.get_config()] = []
                for next_state in self.nfa.transitions[self.current_state]['e']:
                    self.config_dict[self.get_config()].append(('e', next_state))

    def is_accepting_config(self):
        return self.current_state in self.nfa.accepting_states and self.remaining_input == 'e'

    def run_transition(self, letter, next_state):

        if letter == 'e':
            self.current_state = next_state

        elif len(self.remaining_input) == 1:
            self.current_state, self.remaining_input = next_state, 'e'

        else:
            self.current_state, self.remaining_input = next_state, self.remaining_input[1:]

        self.update_config_dict()

    def run_deterministic_transitions(self):
        """
        From a given NFA configuration, runs transitions as long as there is only one available.
        Updates the configuration, and returns Accept/Reject booleans.
        """


        # Check if in an accepting configuration
        if self.is_accepting_config():
            return True, False

        # Check if in a rejecting configuration
        if self.get_config() not in self.config_dict:
            return False, True

        # Check if the next transition is non-deterministic
        if len(self.config_dict[self.get_config()]) > 1:
            return False, False

        # Else, run transition, update the configuration and computation, then recurse.
        letter, state = self.config_dict[self.get_config()][0]
        self.run_transition(letter, state)
        self.computation.append(self.get_config())
        return self.run_deterministic_transitions()

    def run_machine(self):
        """Run the machine on input string"""

        if not self.nfa.is_path_to_accept_state():
            return "No accepting states in this NFA can be reached. Every input will be rejected."
        self.computation.append(self.get_config())
        accept, reject = self.run_deterministic_transitions()

        if accept:
            return "Word accepted!", self.computation
        if reject:
            return "Word rejected!"

        # Else we reached a non-deterministic transition. Use backtracking search algorithm.
        return self.search()

    def search(self, depth=0, path=None):
        if path is None:
            path = []

        # Iterate through possible transitions at given configuration
        for index, (letter, state) in enumerate(self.config_dict[self.get_config()]):

            # Make a copy of the NFAConfiguration object in case we need to backtrack later
            next_self = copy.deepcopy(self)

            # In the copy of the dictionary, remove all other transitions from this configuration
            next_self.config_dict[self.get_config()] = [(letter, state)]
            accept, reject = next_self.run_deterministic_transitions()

            if accept:
                return "Word accepted!", next_self.computation

            if reject:
                if index + 1 == len(self.config_dict[self.get_config()]):
                    if depth == 0:
                        return "Word rejected!"
                    else:
                        # Need to backtrack
                        tried_letter, tried_state, last_current_state, last_remaining_inp, last_computation, last_dict = path.pop()
                        last_self = NFAConfiguration(self.nfa, self.input_string, last_current_state, last_remaining_inp,
                                                     last_computation, last_dict)
                        last_self.config_dict[last_self.get_config()].remove((tried_letter, tried_state))
                        return last_self.search(depth - 1, path)

            if not (accept or reject):
                path.append((letter, state, self.current_state, self.remaining_input, self.computation, self.config_dict))
                return next_self.search(depth + 1, path)


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

# a DFA for 0*
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

# {aa u aab}∗{b}
nfa5 = NFA(
    states={'q0', 'q1', 'q2', 'q3', 'q4'},
    input_alphabet={'a', 'b'},
    transitions={
        'q0': {'a': {'q1', 'q2'}, 'b': {'q4'}},
        'q1': {'a': {'q0'}},
        'q2': {'a': {'q3'}},
        'q3': {'b': {'q0'}}
    },
    initial_state='q0',
    accepting_states={'q4'}
)

nfa6 = NFA(
    states={'q0', 'q1', 'q2', 'q3'},
    input_alphabet={'a', 'b'},
    transitions={
        'q0': {'a': {'q1'}},
        'q1': {'b': {'q3', 'q2'}, 'e': {'q2', 'q1'}},
        'q2': {'e': {'q2'}},
        'q3': {'a': {'q0'}, 'e': {'q3'}}
    },
    initial_state='q0',
    accepting_states={'q3'}
)

# input_str = input("Enter the input string, or type 'Exit': ")
nfa_configuration = NFAConfiguration(nfa, 'aaabaabaaabaaaa')

print(nfa_configuration.run_machine())
