import copy


class PDA:
    def __init__(self, states, input_alphabet, stack_alphabet, transitions,
                 initial_state, initial_stack_symbol):
        """Instantiate NFA object"""
        self.states = states
        self.input_alphabet = input_alphabet
        self.stack_alphabet = stack_alphabet
        self.transitions = transitions
        self.initial_state = initial_state
        self.initial_stack_symbol = initial_stack_symbol

    #     self.check_empty_loops = True
    #     while self.check_empty_loops:
    #         self.check_empty_loops = self.is_empty_loop()
    #
    # def is_empty_loop(self):
    #
    #     for first_state in self.transitions:
    #         for letter in self.transitions[first_state]:
    #             if letter == 'e':
    #                 for next_state in self.transitions[first_state][letter]:
    #                     if next_state == first_state:
    #                         self.transitions[first_state][letter].remove(next_state)
    #                         if len(self.transitions[first_state][letter]) == 0:
    #                             del self.transitions[first_state][letter]
    #                         if not bool(self.transitions[first_state]):
    #                             del self.transitions[first_state]
    #                         return True
    #     return False
    #
    # def is_path_to_accept_state(self):
    #
    #     if len(self.accepting_states) == 0:
    #         return False
    #
    #     if self.initial_state in self.accepting_states:
    #         return True
    #
    #     for state in self.transitions:
    #         for letter in self.transitions[state]:
    #             if len(self.accepting_states.intersection(self.transitions[state][letter])) > 0:
    #                 return True
    #
    #     return False

    def __str__(self):
        return f"States: {self.states} \nInput Alphabet: {self.input_alphabet} \nStack Alphabet: {self.stack_alphabet} \
               \nTransitions: {self.transitions} \nInitial State: {self.initial_state} \nInitial Stack Symbol: {self.initial_stack_symbol}"


class PDAConfiguration:
    def __init__(self, pda, input_string, current_state=None, current_stack=None, remaining_input=None, computation=None, config_dict=None):
        if current_state is None:
            current_state = pda.initial_state
        if current_stack is None:
            current_stack = [pda.initial_stack_symbol]
        if computation is None:
            computation = []
        if remaining_input is None:
            remaining_input = input_string
        if config_dict is None:
            config_dict = dict()

        self.pda = pda
        self.input_string = input_string
        self.current_state = current_state
        self.current_stack = current_stack
        self.remaining_input = remaining_input
        self.computation = computation
        self.config_dict = config_dict
        self.update_config_dict()


    def get_config(self):
        # A PDA configuration is a triple of (current state, remaining input, stack contents)
        return self.current_state, self.remaining_input, self.current_stack

    def get_config_tuple(self):
        return self.current_state, self.remaining_input, tuple(self.current_stack)

    def update_config_dict(self):

        # Updates dictionary which maps configurations of (current state, remaining input, current stack) to a list of
        # available transitions (letter to read, string to push to stack, next state).

        # Only need to update if the configuration is not already in the dictionary and it has an available transition
        if self.get_config_tuple() not in self.config_dict and self.current_state in self.pda.transitions and \
                self.current_stack[0] in self.pda.transitions[self.current_state]:

            # Check for transitions reading the next letter
            if self.remaining_input[0] in self.pda.transitions[self.current_state][self.current_stack[0]]:
                self.config_dict[self.get_config_tuple()] = []
                for next_state, push_stack in self.pda.transitions[self.current_state][self.current_stack[0]][self.remaining_input[0]]:
                    self.config_dict[self.get_config_tuple()].append((self.remaining_input[0], push_stack, next_state))

            # Check for transitions reading 'e'
            if self.remaining_input[0] != 'e' and 'e' in self.pda.transitions[self.current_state][self.current_stack[0]]:
                if self.get_config_tuple() not in self.config_dict:
                    self.config_dict[self.get_config_tuple()] = []
                for next_state, push_stack in self.pda.transitions[self.current_state][self.current_stack[0]]['e']:
                    self.config_dict[self.get_config_tuple()].append(('e', push_stack, next_state))




    def is_accepting_config(self):
        # An accepting configuration is when the stack is empty and remaining input is empty
        return self.current_stack == ['e'] and self.remaining_input == 'e'

    def stack_transition(self, pop_symbol, push_string):
        # A PDA stack is given by a list of stack symbols with the top at the head. For any transition, remove
        # pop_symbol from the head and append each symbol from the push_string to the top in reverse order.
        # Empty cases: if the pop_symbol is 'e', don't remove anything. If the push_string is 'e', don't append
        # anything.

        if len(self.current_stack) == 0:
            print("Error. Stack already empty")
            return

        if self.current_stack[0] != pop_symbol:
            print("Error. Symbol to pop is not on the stack.")
            return

        # Pop:
        if len(self.current_stack) == 1:
            self.current_stack = ['e']
        else:
            self.current_stack = self.current_stack[1:]

        # Push:
        if push_string == 'e':
            return
        else:
            for symbol in reversed(push_string):
                self.current_stack.insert(0, symbol)

        if len(self.current_stack) > 1 and self.current_stack[-1] == 'e':
            self.current_stack = self.current_stack[:-1]

    def run_transition(self, letter, next_state, pop_symbol, push_string):

        # Update state and read letter
        if letter == 'e':
            self.current_state = next_state

        elif len(self.remaining_input) == 1:
            self.current_state, self.remaining_input = next_state, 'e'

        else:
            self.current_state, self.remaining_input = next_state, self.remaining_input[1:]

        # Update stack
        self.stack_transition(pop_symbol, push_string)

        self.update_config_dict()

    def run_deterministic_transitions(self):
        """
        From a given PDA configuration, runs transitions as long as there is only one available.
        Updates the configuration, and returns Accept/Reject booleans.
        """


        # Check if in an accepting configuration
        if self.is_accepting_config():
            return True, False

        # Check if in a rejecting configuration
        if self.get_config_tuple() not in self.config_dict:
            return False, True

        # Check if the next transition is non-deterministic
        if len(self.config_dict[self.get_config_tuple()]) > 1:
            return False, False

        # Else, run transition, update the configuration and computation, then recurse.
        letter, push_string, state = self.config_dict[self.get_config_tuple()][0]
        self.run_transition(letter, state, self.current_stack[0], push_string)
        self.computation.append(self.get_config())
        return self.run_deterministic_transitions()



pda = PDA(
    states={'q0', 'q1', 'q2', 'q3'},
    input_alphabet={'a', 'b'},
    stack_alphabet={'Z', 'a'},
    transitions={
        'q0':                         # Start state
            {'Z':                     # Stack symbol to pop
                 {'a':                # Letter to read
                      {('q1', 'aZ')}  # Set of (next state, stack string to push) transitions. If only one, deterministic transition.
                  }
             },
        'q1':
            {'a':
                 {'a':
                      {('q1', 'aa')},
                  'b' : {('q2', 'e')}
                  },

             },
        'q2':
            {'a':
                 {'b':
                      {('q2', 'e')}
                  },
             'Z':
                 {'e':
                      {('q3', 'e')}
                  }
             }
    },
    initial_state='q0',
    initial_stack_symbol='Z'
)

pda_config = PDAConfiguration(pda, 'aaabbb')


print(pda_config.run_deterministic_transitions())
print(pda_config.computation)
