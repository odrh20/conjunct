import copy
from Leaf import Leaf
from Internal import Internal


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


class SAPDAConfiguration:
    def __init__(self, sapda, input_string, current_state=None, current_stack=None, remaining_input=None,
                 computation=None, config_dict=None):
        if current_state is None:
            current_state = sapda.initial_state
        if current_stack is None:
            current_stack = [sapda.initial_stack_symbol]
        if computation is None:
            computation = []
        if remaining_input is None:
            remaining_input = input_string
        if config_dict is None:
            config_dict = dict()

        self.sapda = sapda
        self.input_string = input_string
        self.current_state = current_state
        self.current_stack = current_stack
        self.remaining_input = remaining_input
        self.computation = computation
        self.config_dict = config_dict


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

internal = Internal(sapda1, ['Z'])

print(internal.current_stack)

leaf = Leaf(sapda1, ['X'], 'q0', 'abc', 'aabbcc')

print(leaf.remaining_input)


print(internal.get_config())
print(leaf.get_config())


