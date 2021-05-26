# Class for leaf (active) nodes which inherits from the Node class.
# Leaves are active and need to be processed. They are labelled by a triple of (current state, remaining input, stack).

from Node import Node


class Leaf(Node):
    def __init__(self, sapda, tree, current_stack, current_state, remaining_input):
        self.current_state = current_state
        self.input_string = tree.input_string
        self.remaining_input = remaining_input
        super().__init__(sapda, tree, current_stack)

    def get_config(self):
        return self.current_state, self.remaining_input, self.current_stack

    def get_config_tuple(self):
        return self.current_state, self.remaining_input, tuple(self.current_stack)

    def update_config_dict(self):

        # Updates dictionary which maps configurations of (current state, remaining input, current stack) to a list of
        # available transitions (letter to read, string to push to stack, next state).

        # Only need to update if the configuration is not already in the dictionary and it has an available transition
        if self.get_config_tuple() not in self.tree.config_dict and self.current_state in self.sapda.transitions and \
                self.current_stack[0] in self.sapda.transitions[self.current_state]:

            # Check for transitions reading the next letter
            if self.remaining_input[0] in self.sapda.transitions[self.current_state][self.current_stack[0]]:
                self.tree.config_dict[self.get_config_tuple()] = []
                for next_state, push_stack in self.sapda.transitions[self.current_state][self.current_stack[0]][
                    self.remaining_input[0]]:
                    self.tree.config_dict[self.get_config_tuple()].append((self.remaining_input[0], push_stack, next_state))

            # Check for transitions reading 'e'
            if self.remaining_input[0] != 'e' and 'e' in self.sapda.transitions[self.current_state][
                self.current_stack[0]]:
                if self.get_config_tuple() not in self.tree.config_dict:
                    self.tree.config_dict[self.get_config_tuple()] = []
                for next_state, push_stack in self.sapda.transitions[self.current_state][self.current_stack[0]]['e']:
                    self.tree.config_dict[self.get_config_tuple()].append(('e', push_stack, next_state))

    def has_empty_stack(self):
        # When a SAPDA leaf empties its stack, it cannot be processed any further.
        return self.current_stack == ['e']

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
        From a given SAPDA leaf configuration, runs transitions as long as there is only one available.
        Updates the configuration, and returns Processed/Reject booleans.
        """

        # A leaf is processed if it empties its stack
        if self.has_empty_stack():
            return True, False

        # If stack has not emptied and there are no available transitions, SAPDA rejects input string
        if self.get_config_tuple() not in self.tree.config_dict:
            return False, True

        # Reject if leaf has read the entire input string, stack is not empty, and no available 'e' transitions
        if self.remaining_input == 'e' and (not self.has_empty_stack()) and 'e' not in self.sapda.transitions[self.current_state][self.current_stack[0]]:
            return False, True

        # Halt loop if a non-deterministic transition is encountered
        if len(self.tree.config_dict[self.get_config_tuple()]) > 1:
            return False, False

        # Else, run transition, update the configuration and computation, then recurse.
        letter, push_string, state = self.tree.config_dict[self.get_config_tuple()][0]
        self.run_transition(letter, state, self.current_stack[0], push_string)
        return self.run_deterministic_transitions()

    # def run_machine(self):
    #     """Run the machine on input string"""
    #
    #     self.computation.append(self.get_config())
    #     accept, reject = self.run_deterministic_transitions()
    #
    #     if accept:
    #         return "Word accepted!", self.computation
    #     if reject:
    #         return "Word rejected!"
    #
    #     # Else we reached a non-deterministic transition. Use backtracking search algorithm.
    #     return self.search()
    #
    # def search(self, depth=0, path=None):
    #     if path is None:
    #         path = []
    #
    #     # Iterate through possible transitions at given configuration
    #     for index, (letter, push_string, state) in enumerate(self.config_dict[self.get_config_tuple()]):
    #
    #         # Make a copy of the NFAConfiguration object in case we need to backtrack later
    #         next_self = copy.deepcopy(self)
    #
    #         # In the copy of the dictionary, remove all other transitions from this configuration
    #         next_self.config_dict[self.get_config_tuple()] = [(letter, push_string, state)]
    #         accept, reject = next_self.run_deterministic_transitions()
    #
    #         if accept:
    #             return "Word accepted!", next_self.computation
    #
    #         if reject:
    #             if index + 1 == len(self.config_dict[self.get_config_tuple()]):
    #                 if depth == 0:
    #                     return "Word rejected!"
    #                 else:
    #                     # Need to backtrack
    #                     tried_letter, tried_push, tried_state, last_current_state, last_current_stack, last_remaining_inp, last_computation, last_dict = path.pop()
    #                     last_self = PDAConfiguration(self.pda, self.input_string, last_current_state, last_current_stack, last_remaining_inp, last_computation, last_dict)
    #                     last_self.config_dict[last_self.get_config_tuple()].remove((tried_letter, tried_push, tried_state))
    #                     return last_self.search(depth - 1, path)
    #
    #         if not (accept or reject):
    #             path.append((letter, push_string, state, self.current_state, self.current_stack, self.remaining_input, self.computation, self.config_dict))
    #             return next_self.search(depth + 1, path)
