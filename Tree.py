# Class representing the entire configuration of the SAPDA.

from SAPDA import SAPDA
from Leaf import Leaf
from Internal import Internal


class Tree:
    def __init__(self, sapda, input_string, computation=None, config_dict=None):
        if computation is None:
            computation = []
        if config_dict is None:
            config_dict = dict()

        self.sapda = sapda
        self.input_string = input_string
        self.computation = computation
        self.config_dict = config_dict

    def get_initial_leaf(self):
        return Leaf(self.sapda, self, [self.sapda.initial_stack_symbol], self.sapda.initial_state, self.input_string)





