from Derivation import *
from Word import *
from CG import *
import numpy as np
import pandas as pd
from tabulate import tabulate
import sys
sys.setrecursionlimit(10**6)

large_width = 400
np.set_printoptions(linewidth=large_width)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)


class Parser:

    def __init__(self, grammar, word, table=None):
        self.grammar = grammar
        self.grammar.convert_to_BNF()
        self.word = word
        self.n = len(self.word)
        if table is None:
            self.table = np.empty([self.n, self.n], dtype=set)
        else:
            self.table = table

    def join_nodes(self, node_1, node_2):
        """
        Combine a left node and a down node to get a pointer: a two-variable conjunct (A,B) and the positions of both
        nodes.
        """
        return (node_1.variable+node_2.variable), (node_1.i, node_1.j), (node_2.i, node_2.j)

    def get_possible_pointers(self, set_1, set_2):
        """
        Take a set of left nodes and down nodes, combine them in all combinations to get a set of pointers.
        """
        pointers = set()
        for node_1 in set_1:
            for node_2 in set_2:
                pointers.add(self.join_nodes(node_1, node_2))
        return pointers

    def get_node_set(self, pointers, i, j):
        """
        Given a set of possible pointers, and a position in the matrix, check if there is a rule in the grammar where
        all conjuncts are in the pointer set. If so, add a Node in the current position.
        """
        node_set = set()
        conjunct_set = set()
        for conjunct, _, _ in pointers:
            conjunct_set.add(conjunct)

        rule_set = set()
        for variable in self.grammar.rules:
            for expansion in self.grammar.rules[variable]:
                if all(conjunct in conjunct_set for conjunct in expansion):
                    rule_set.add((variable, expansion))

        for var, expansion in rule_set:
            new_node = Node(i, j, var)
            for conjunct in expansion:
                for (conj, left_pos, right_pos) in pointers:
                    if conjunct == conj:
                        new_node.update_pointers(conjunct, left_pos, right_pos)
                        node_set.add(new_node)

        return node_set

    def recognise_word(self):
        """
        Returns True if the word is in the language, and False if not.
        """
        if self.word == 'e':
            return ('e',) in self.grammar.rules[self.grammar.start_variable]

        self.populate_table()
        print(self)

        return self.grammar.start_variable in self.table[0, self.n-1]

    def populate_table(self):
        self.compute_diagonal()

        for k in range(self.n):
            for i in range(self.n-k):
                j = k + i
                node_set = set()
                for m in range(i, j):
                    new_nodes = self.get_possible_pointers(self.table[i, m], self.table[m+1, j])
                    node_set = node_set.union(new_nodes)
                    self.table[i, j] = self.get_node_set(node_set, i, j)
                    #print(f"Updating table at index {i,j}")
                    #self.table[i, j] = self.f(R)

        for node in list(self.table[0, self.n-1]):
            if node.variable != self.grammar.start_variable:
                self.table[0, self.n - 1].remove(node)

    def compute_diagonal(self):
        for i in range(self.n):
            self.table[i, i] = set()
            for variable in self.grammar.rules:
                if (self.word[i],) in self.grammar.rules[variable]:
                    new_node = Node(i, i, variable)
                    new_node.update_pointers(self.word[i], None, None)
                    self.table[i, i].add(new_node)

    def __str__(self):
        """
        Uses tabulate to generate a recognition matrix for printing.
        """
        data = copy.deepcopy(self.table)

        for i in range(self.n):
            for j in range(self.n):
                if data[i, j] is not None and len(data[i, j]) > 0:
                    for node in data[i, j]:
                        data[i, j].remove(node)
                        data[i, j].add(str(node))

        data = np.where(data is None, '', data)
        data = np.where(data == set(), '{}', data)

        #return tabulate(data, headers=[('\033[91m' + letter + '\033[0m') for letter in self.word], tablefmt='psql')


        if self.grammar.start_variable in data[0, self.n - 1]:
            data[0, self.n - 1] = '\033[92m' + str(data[0, self.n - 1]) + '\033[0m'

        else:
            data[0, self.n - 1] = '\033[91m' + str(data[0, self.n - 1]) + '\033[0m'

        return tabulate(data, headers=[('\033[91m' + letter + '\033[0m') for letter in self.word], tablefmt='psql')

    def find_parse(self, d=None):
        """
        From a completed recognition matrix, start in the top-right corner with the start variable and work towards
        the diagonal to find a derivation path.
        Use Derivation class to store the derivation path, which is a list of triples (latest word, last rule, index).
        The latest word is a Word object which contains an index dictionary, keeping track of the current position of
        each variable.
        """
        if d is None:  # Initialise a new derivation.
            d = Derivation(self.grammar, self.word)
        #print(d.derivation)

        #latest_word = d.get_latest_word()  # latest Word object in derivation
        #active_var, idx, (i, j) = latest_word.get_var_index_pos()  # First variable in current word, to do rule step

        #return active_var, idx, i, j
        # i, j = latest_word.get_matrix_position(i)  # Position in matrix of active variable.
        #
        while d.get_latest_word().current_word != self.word:
            active_var, idx, (i, j) = d.get_latest_word().get_var_index_pos()
            for node in self.table[i, j]:
                if node.variable == active_var:
                    expansion = node.get_expansion()
                    #print("expansion: ", expansion)
                    d.derivation += d.get_latest_word().apply_rule(active_var, expansion, idx)
                    d.get_latest_word().update_variable_tracker(node)
                    #print(d.get_latest_word())


        #
        return d.print_derivation()
        #return str(d)

"""
Cells in a recognition matrix contain sets of Node objects.
Each Node corresponds to a specific position in the matrix and a single rule to follow, which may contain more than one
conjunct.
The pointer dictionary shows where the rule points to for each conjunct, in left and downward directions for both
variables in a two-variable rule.
If the Node is on the diagonal, then the rule goes to a single terminal and the pointers are None values.
"""


class Node:
    def __init__(self, i, j, variable, pointers=None):
        self.i = i
        self.j = j
        self.variable = variable
        if pointers is None:
            self.pointers = set()

    def update_pointers(self, conjunct, left_pos, down_pos):
        self.pointers.add((conjunct, left_pos, down_pos))

    def get_expansion(self):
        expansion = []
        for conjunct, _, _ in self.pointers:
            expansion.append(conjunct)
        return tuple(expansion)

    def __repr__(self):
        return self.variable

        # print_string = self.variable
        # for ele in self.pointers:
        #     print_string += str(ele)
        # return print_string

    # def __eq__(self, other):
    #     if isinstance(other, Node):
    #         return self.i == other.i and self.j == other.j and self.variable == other.variable and self.pointers == \
    #             other.pointers
    #
    # def __hash__(self):
    #     return hash((self.i, self.j, self.variable, tuple(self.pointers)))

p = Parser(cg6, 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')

p.compute_diagonal()

p.populate_table()

print(p)

print(p.find_parse())
