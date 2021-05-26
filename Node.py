# Abstract base class for nodes of a SAPDA configuration.
# Each node is either a Leaf (an active node) or a Root (internal node).

from abc import ABC, abstractmethod


class Node(ABC):
    def __init__(self, sapda, current_stack):
        self.sapda = sapda
        self.current_stack = current_stack

    @abstractmethod
    def get_config(self):
        pass


