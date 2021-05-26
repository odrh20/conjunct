# Class for leaf (active) nodes which inherits from the Node class.
# Leaves are active and need to be processed. They are labelled by a triple of (current state, remaining input, stack).

from Node import Node


class Leaf(Node):
    def __init__(self, sapda, current_stack, current_state, input_string, remaining_input):
        self.current_state = current_state
        self.input_string = input_string
        self.remaining_input = remaining_input
        super().__init__(sapda, current_stack)

    def get_config(self):
        return self.current_state, self.remaining_input, self.current_stack

