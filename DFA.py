class DFA:
    def __init__(self, states, input_alphabet, transitions,
                 initial_state, accepting_states):
        """Instantiate DFA object"""
        self.states = states
        self.input_alphabet = input_alphabet
        self.transitions = transitions
        self.initial_state = initial_state
        self.accepting_states = accepting_states
        self.current_state = self.initial_state

    def run_state_transition(self, input_letter):
        """Takes in current state and goes to next state based on input symbol."""
        #print("CURRENT STATE : {}\tINPUT LETTER : {}\t NEXT STATE : {}".format(self.current_state, input_letter,
                                                                               #self.transitions[self.current_state][
                                                                                   #input_letter]))
        self.current_state = self.transitions[self.current_state][input_letter]
        return self.current_state

    def check_if_accept(self):
        """Checks if the current state is one of the accept states."""
        return self.current_state in self.accepting_states

    def run_machine(self, input_string):
        """Run the machine on input string"""
        computation = []
        for i in range(len(input_string)):
            computation.append((self.current_state, input_string[i:]))
            self.run_state_transition(input_string[i])

        if not self.check_if_accept():
            return "Input string rejected."
        else:
            computation.append((self.current_state, 'e'))
            return "Input string accepted. Computation: ", computation




# DFA which matches all binary strings ending in an odd number of '1's
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

print(dfa.transitions['q0']['0'])

#input_str = input("Enter the input string : ")
#print(dfa.run_machine(input_str))

# test_set = {'a', 'b', 'c', 'd'}
# new_set = set()
# for value in test_set:
#     new_set.add((1, value))
# test_set2 = {'e', 'f', 'g', 'h'}
# new_set2 = set()
# for value in test_set2:
#     new_set2.add((2, value))
#
# print(new_set)
# print(new_set2)
# merged_set = new_set.union(new_set2)
# print(merged_set)
# states: set of strings
# input_alphabet: set of strings
# transitions: a dict consisting of the transitions for each state. Each key is a state name and each value is a dict which maps a symbol (the key) to a state (the value).
# initial_state: the name of the initial state for this DFA
#final_states: a set of final states for this DFA

