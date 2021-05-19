class DFA:
    def __init__(self, states, input_alphabet, transitions,
                 initial_state, accepting_states):
        """Instantiate NFA object"""
        self.states = states
        self.input_alphabet = input_alphabet
        self.transitions = transitions
        self.initial_state = initial_state
        self.accepting_states = accepting_states
        self.current_state = None

    def run_state_transition(self, input_letter):
        """Takes in current state and goes to next state based on input symbol."""
        print("CURRENT STATE : {}\tINPUT LETTER : {}\t NEXT STATE : {}".format(self.current_state, input_letter,
                                                                               self.transitions[self.current_state][
                                                                                   input_letter]))
        self.current_state = self.transitions[self.current_state][input_letter]
        return self.current_state

    def check_if_accept(self):
        """Checks if the current state is one of the accept states."""
        return self.current_state in self.accepting_states

    def run_machine(self, input_string):
        """Run the machine on input string"""
        self.current_state = self.initial_state
        computation = []
        for ele in in_string:
            check_state = self.run_state_transition(ele)
            # Check if new state is not REJECT
            if (check_state == 'REJECT'):
                return False
        return self.check_if_accept()


dfa = DFA(
    states={'q0', 'q1', 'q2'},
    input_alphabet={'0', '1'},
    transitions={
        'q0': {'0': 'q0', '1': 'q1'},
        'q1': {'0': 'q0', '1': 'q2'},
        'q2': {'0': 'q2', '1': 'q1'}
    },
    initial_state='q0',
    accepting_states={'q1'}
)



# states: set of strings
# input_alphabet: set of strings
# transitions: a dict consisting of the transitions for each state. Each key is a state name and each value is a dict which maps a symbol (the key) to a state (the value).
# initial_state: the name of the initial state for this DFA
#final_states: a set of final states for this DFA

