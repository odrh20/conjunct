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


