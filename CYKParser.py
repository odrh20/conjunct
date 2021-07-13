from Word_ import *
from Derivation_ import *
from Derivation import *
from Word import *
from CG import *
import numpy as np
import pandas as pd
from IPython.display import display
from tabulate import tabulate


large_width = 400
np.set_printoptions(linewidth=large_width)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)





class CYKParser:

    def __init__(self, grammar, word, table=None):
        self.grammar = grammar
        self.grammar.convert_to_BNF()
        self.word = word
        self.n = len(self.word)
        if table is None:
            self.table = np.empty([self.n, self.n], dtype=set)
        else:
            self.table = table

    @staticmethod
    def get_cartesian_product(set_1, set_2):
        new_set = set()
        for i in set_1:
            for j in set_2:
                new_set.add(i+j)
        return new_set

    def f(self, R):
        """
        Given a set R of two-variable conjuncts, return a set of variables in the grammar which have a rule where
        each conjunct belongs to R.
        """
        new_set = set()
        for variable in self.grammar.rules:
            for expansion in self.grammar.rules[variable]:
                if all(conjunct in R for conjunct in expansion):
                    new_set.add(variable)
                    break
        return new_set

    def recognise_word(self):
        """
        Returns True if the word is in the language, and False if not.
        """
        if self.word == 'e':
            return ('e',) in self.grammar.rules[self.grammar.start_variable]

        self.populate_table()
        print(self.print_table())

        return self.grammar.start_variable in self.table[0, self.n-1]

    def populate_table(self):
        self.compute_diagonal()

        for k in range(self.n):
            for i in range(self.n-k):
                j = k + i
                R = set()
                for m in range(i, j):
                    new_conjuncts = self.get_cartesian_product(self.table[i, m], self.table[m+1, j])
                    R = R.union(new_conjuncts)
                    #print(f"Updating table at index {i,j}")
                    self.table[i, j] = self.f(R)


    def compute_diagonal(self):
        for i in range(self.n):
            self.table[i, i] = set()
            for variable in self.grammar.rules:
                if (self.word[i],) in self.grammar.rules[variable]:
                    self.table[i, i].add(variable)

    def print_table(self):
        """
        Uses tabulate to generate a recognition matrix for printing.
        """
        data = copy.deepcopy(self.table)
        data = np.where(data is None, '', data)
        data = np.where(data == set(), '{}', data)
        if self.grammar.start_variable in data[0, p.n - 1]:
            data[0, p.n - 1] = '\033[92m' + str(data[0, p.n - 1]) + '\033[0m'

        else:
            data[0, p.n - 1] = '\033[91m' + str(data[0, p.n - 1]) + '\033[0m'

        return tabulate(data, headers=[('\033[91m' + letter + '\033[0m') for letter in self.word], tablefmt='psql')

    @staticmethod
    def get_indices(i, j):
        """
        For constructing a derivation from a completed recognition matrix.
        Given the current position in the matrix, return two lists: one for the positions to the left, and one for the
        positions below.
        """
        left = []
        for k in range(j-1, i-1, -1):
            left.append((i, k))

        below = []
        for m in range(i+1, j+1):
            below.append((m, j))

        return left, below

    def get_reachable_expansions(self, i, j):
        """
        From a given position in the recognition matrix, scan left and below to generate set of possible rule
        expansions.
        Return a dictionary with
        """
        left_indices, below_indices = self.get_indices(i, j)
        left_vars = set()
        for r, c in left_indices:
            left_vars = left_vars.union(self.table[r, c])

        below_vars = set()
        for r, c in below_indices:
            below_vars = below_vars.union(self.table[r, c])

        return self.get_cartesian_product(left_vars, below_vars)

        # expansion_dict = dict()
        # for expansion in expansions:
        #     for (a, b) in left_indices:
        #         for (c, d) in below_indices:
        #             if expansion[0] in self.table[a, b] and expansion[1] in self.table[c, d]:
        #                 if (a, b, c, d) not in expansion_dict:
        #                     expansion_dict[(a, b, c, d)] = set()
        #                 expansion_dict[(a, b, c, d)].add(expansion)


    def find_parse(self):
        """
        From a completed recognition matrix, start in the top-right corner with the start variable and work towards
        the diagonal to find a derivation path.
        Use Derivation class to store the derivation path, which is a list of triples (latest word, last rule, index).
        The latest word is a Word object which contains an index dictionary, keeping track of the current position of
        each variable.
        First initialise a new Derivation.
        """
        d = Derivation(self.grammar, self.word)
        self.table[0, self.n-1] = {self.grammar.start_variable}

        latest_word = d.get_latest_word()  # latest Word object in the Derivation
        var_index = d.get_latest_word().get_first_var_index()
        active_var = latest_word.current_word[var_index]  # First var found in latest word.
        i, j = latest_word.get_matrix_position(var_index)  # Position in matrix of active variable.

        return self.get_reachable_expansions(i, j)

"""
Cells in a recognition matrix contain sets of Node objects.
Each Node corresponds to a specific position in the matrix and a single rule to follow, which may contain more than one
conjunct.
The pointer dictionary shows where the rule points to for each conjunct, in left and downward directions for both
variables in a two-variable rule.
If the Node is on the diagonal, then the rule goes to a single terminal and the pointers are None values.
"""


class Node:
    def __init__(self, i, j, pointer_dict=None):
        self.i = i
        self.j = j
        if pointer_dict is None:
            self.pointer_dict = dict()
        self.pointer_dict = pointer_dict

    def update_pointer_dict(self, conjunct, left_pos, down_pos):
        self.pointer_dict[conjunct] = (left_pos, down_pos)





p = CYKParser(cg3, 'abbaa$abbaa')
print(p.recognise_word())

print(p.find_parse())
