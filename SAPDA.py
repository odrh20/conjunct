


class SAPDA:
    def __init__(self, states, input_alphabet, stack_alphabet, transitions,
                 initial_state, initial_stack_symbol):
        """Instantiate SAPDA object"""
        self.states = states
        self.input_alphabet = input_alphabet
        self.stack_alphabet = stack_alphabet
        self.transitions = transitions
        self.initial_state = initial_state
        self.initial_stack_symbol = initial_stack_symbol

    def __str__(self):
        return f"States: {self.states} \nInput Alphabet: {self.input_alphabet} \nStack Alphabet: {self.stack_alphabet} \
               \nTransitions: {self.transitions} \nInitial State: {self.initial_state} \nInitial Stack Symbol: {self.initial_stack_symbol}"


# words with equal number of a's, b's and c's
sapda1 = SAPDA(
    states={'q0', 'q1', 'q2'},
    input_alphabet={'a', 'b', 'c'},
    stack_alphabet={'Z', 'a', 'b', 'c'},
    transitions={
        'q0': {'Z': {'e': {(('q1', 'Z'), ('q2', 'Z'))}}
               },
        'q1': {'Z': {'a': {('q1', 'aZ')}, 'b': {('q1', 'bZ')}, 'c': {('q1', 'Z')}, 'e': {('q0', 'e')}},
               'a': {'a': {('q1', 'aa')}, 'b': {('q1', 'e')}, 'c': {('q1', 'a')}},
               'b': {'a': {('q1', 'e')}, 'b': {('q1', 'bb')}, 'c': {('q1', 'b')}},
               },
        'q2': {'Z': {'a': {('q2', 'Z')}, 'b': {('q2', 'bZ')}, 'c': {('q2', 'cZ')}, 'e': {('q0', 'e')}},
               'b': {'a': {('q2', 'b')}, 'b': {('q2', 'bb')}, 'c': {('q2', 'e')}},
               'c': {'a': {('q2', 'c')}, 'b': {('q2', 'e')}, 'c': {('q2', 'cc')}},
               },
    },
    initial_state='q0',
    initial_stack_symbol='Z'
)

print(sapda1)
