# Class for internal nodes which inherits from the Node class.
# Internal nodes are not active and cannot be processed. They are labelled only by their stack.

from Node import Node


class Internal(Node):
    def __init__(self, sapda, tree, current_stack):
        super().__init__(sapda, tree, current_stack)

    def get_config(self):
        return self.current_stack

    def __str__(self):
        return self.current_stack



