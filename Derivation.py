import copy
import random
from CG import *
from Word import *
#from Parser import *
from tabulate import tabulate

import sys
sys.setrecursionlimit(10**6)



"""
Class for Conjunctive Grammar derivations.
The derivation is represented by a list. At each step, a triple of current_word, rule, and index where rule was
applied is appended to the list.
Rules are represented by a pair of variable, and a tuple of conjuncts. eg. ('S', ('A', 'C')) = S -> A & C
"""


class Derivation:

    def __init__(self, grammar, target_word, derivation=None):
        self.grammar = grammar
        self.target_word = target_word

        if derivation is None:
            start_word = Word(self.grammar, self.grammar.start_variable, self.target_word)
            self.derivation = [(start_word, None, [])]
        else:
            self.derivation = derivation

    def __str__(self):
        return str([(str(word), rule, index) for word, rule, index in self.derivation])

    def get_latest_word(self):
        return self.derivation[-1][0]

    def print_derivation(self):
        """
        Prints each step in the derivation, to be called when derivation of the input string is complete.
        """

        print_string = "\n"
        print_string += f"[u]Derivation for {self.target_word}:[/u]\n\n"
        for i, word in enumerate(self.get_derivation_list()):
            if i != 0:
                print_string += "\n" #[color=ffff00]=>[/color]\n"
            print_string += word
        return print_string

    def get_derivation_list(self):
        """
        Highlight the symbols in the string where a rule was applied in red and return string.
        """
        derivation_words = []

        for i in range(len(self.derivation)):

            if i == len(self.derivation) - 1:
                derivation_words.append('[color=40ff00]' + self.derivation[i][0].current_word + '[/color]')

            else:
                deriv_word = ''
                rule_indices = self.derivation[i+1][2]

                for j in range(len(self.derivation[i][0].current_word)):
                    if j in rule_indices:
                        deriv_word += '[color=ff3333]' + self.derivation[i][0].current_word[j] + '[/color]'
                    else:
                        deriv_word += self.derivation[i][0].current_word[j]
                derivation_words.append(deriv_word)

        return derivation_words

    def derivation_complete(self):
        return self.get_latest_word().word == self.target_word
