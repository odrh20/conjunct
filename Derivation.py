import copy
import random
from CG import *
from Word import *
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
        print("\n")
        print(f"\033[4mDerivation for {self.target_word}:\n\033[0m")
        for word in self.bold_derivations():
            print(word, "\n")
        print("\nDerivation successful!\n")
        return ""

    def bold_derivations(self):
        """
        Highlight the symbols in the string where a rule was applied in red and return string.
        """
        bold_words = []

        for i in range(len(self.derivation)):

            if i == len(self.derivation) - 1:
                bold_words.append('\033[92m' + self.derivation[i][0].current_word + '\033[0m')

            else:
                bold_word = ''
                bold_indices = self.derivation[i+1][2]

                for j in range(len(self.derivation[i][0].current_word)):
                    if j in bold_indices:
                        bold_word += '\033[91m' + self.derivation[i][0].current_word[j] + '\033[0m'
                    else:
                        bold_word += self.derivation[i][0].current_word[j]
                bold_words.append(bold_word)

        return bold_words

    def derivation_complete(self):
        return self.get_latest_word().word == self.target_word


