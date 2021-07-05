import copy
import random
from CG import *
from Word import *
import queue
from queue import PriorityQueue, Queue
from func_timeout import func_timeout, FunctionTimedOut, func_set_timeout
from prompt_toolkit import print_formatted_text, HTML



"""
Class for Conjunctive Grammar derivations.
The derivation is represented by a list. At each step, a triple of current_word, rule, and index where rule was
applied is appended to the list.
Rules are represented by a pair of variable, and a tuple of conjuncts. eg. ('S', ('A', 'C')) = S -> A & C
"""


class Derivation:

    def __init__(self, grammar, target_word, derivation=None, current_word=None):
        self.grammar = grammar
        self.target_word = target_word
        if current_word is None:
            self.current_word = Word(self.grammar, self.grammar.start_variable)
        else:
            self.current_word = current_word

        if derivation is None:
            self.derivation = [(self.grammar.start_variable, None, [])]
        else:
            self.derivation = derivation

    def get_current_word(self):
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
                bold_words.append('\033[92m' + self.derivation[i][0] + '\033[0m')

            else:
                bold_word = ''
                bold_indices = self.derivation[i+1][2]

                for j in range(len(self.derivation[i][0])):
                    if j in bold_indices:
                        bold_word += '\033[91m' + self.derivation[i][0][j] + '\033[0m'
                    else:
                        bold_word += self.derivation[i][0][j]
                bold_words.append(bold_word)

        return bold_words

    def get_terminal_substrings(self, active_string=None, terminal_strings=None):
        """
        Scan current word left to right, and check each string of consecutive terminals, ignoring brackets.
        Return False if any terminal string is not found in the target word. Else, return True.
        """
        if active_string is None:
            active_string = self.current_word.get_word()
        if terminal_strings is None:
            terminal_strings = []

        if not any(symbol in self.grammar.terminals for symbol in active_string):
            return terminal_strings
        i = 0
        while i < len(active_string):
            if active_string[i] in cg1.terminals:
                substring = active_string[i]
                if i < len(active_string):
                    for j in range(i + 1, len(active_string)):
                        if active_string[j] in cg1.terminals:
                            substring += active_string[j]

                        elif active_string[j] in {'(', ')'}:
                            continue
                        else:
                            terminal_strings.append(substring)
                            active_string = active_string[j + 1:]
                            return self.get_terminal_substrings(active_string, terminal_strings)
                    terminal_strings.append(substring)
                    break
            i += 1
        return terminal_strings

    def substring_not_in_target(self):
        return any(self.target_word.get_word().find(substring) == -1 for substring in self.get_terminal_substrings())

    def get_priority(self):
        """
        In the search, prioritise derivations with the longest string of terminals in the current word.
        """
        max_len = 0.5
        for substring in self.get_terminal_substrings():
            if len(substring) > max_len:
                max_len = len(substring)
        return 1 / max_len

    def too_many_terminals_in_conjunct(self):
        for conjuncts in self.current_word.get_conjunct_list():
            for conjunct in conjuncts:
                terminal_count = 0
                for symbol in conjunct:
                    if symbol in self.grammar.terminals:
                        terminal_count += 1
                if terminal_count > len(self.target_word.get_word()):
                    #print(f"TOO MANY TERMINALS IN {conjunct}")
                    return True
        return False

    def derivation_complete(self):
        return self.current_word.get_word() == self.target_word.get_word()

    def derivation_failed(self):
        """
        If there are no variables left in the current string, and this is not the target string, then the derivation
        has failed.
        If
        This function could be expanded on to find derivations sooner that cannot possibly lead to the target string.
        """
        #print("current word: ", self.get_current_word())
        #print("current conjunct list: ", self.current_word.get_conjunct_list())
        if self.derivation_complete():
            return False

        if len(self.current_word.get_terminal_variable_string()) > 0:
            first_letter = self.current_word.get_terminal_variable_string()[0]
            last_letter = self.current_word.get_terminal_variable_string()[-1]
            if first_letter in self.grammar.terminals and first_letter != self.target_word.get_word()[0]:
                #print("\n DERIVATION FAILED BECAUSE FIRST LETTER IS A TERMINAL WHICH IS NOT THE FIRST LETTER OF TARGET\n")
                return True
            if last_letter in self.grammar.terminals and last_letter != self.target_word.get_word()[-1]:
                #print("\n DERIVATION FAILED BECAUSE LAST LETTER IS A TERMINAL WHICH IS NOT THE LAST LETTER OF TARGET\n")
                return True

        if self.substring_not_in_target():
            #print("\nDERIVATION FAILED BECAUSE FOUND A TERMINAL SUBSTRING NOT IN THE TARGET WORD\n")
            return True

        if self.too_many_terminals_in_conjunct():
            #print("\nDERIVATION FAILED BECAUSE TOO MANY TERMINALS IN ONE CONJUNCT\n")
            return True

        # if len(self.current_word.get_terminal_string()) > len(self.target_word.get_word()):
        #     print("\n DERIVATION FAILED BECAUSE THERE ARE MORE TERMINALS IN CURRENT WORD THAN IN TARGET\n")
        #     return True

        if not self.current_word.has_variables():
            #print("\n DERIVATION FAILED BECAUSE CURRENT WORD HAS NO VARIABLES\n")
            return True

        return False

    def get_derivation(self):
        #for var in self.grammar.rules:
            #print(self.grammar.rules[var])
        if self.target_word.get_word() == 'e' and not any(('e',) in self.grammar.rules[var] for var in self.grammar.rules):
            return "Word rejected!!"

        if self.target_word.get_word() != 'e' and any(letter not in self.grammar.terminals for letter in self.target_word.get_word()):
            return "Word rejected!"

        return self.bfs()

    def bfs(self):
        paths = PriorityQueue()
        paths.put((self.get_priority(), id(self), self))
        #for priority, _, item in list(paths.queue):
            #print(f"Priority {priority}, Current word {item.current_word}")

        while not paths.empty():

            _, _, current_self = paths.get()
            #print("Current self from queue: ", current_self.current_word)
            #print("\nSubstrings of terminals in current word: ", current_self.get_terminal_substrings())
            #print("\nvariables in current word: ", current_self.current_word.get_current_variables())
            for var, _, index in current_self.current_word.get_current_variables():
                for expansion in current_self.grammar.rules[var]:
                    new_self = copy.deepcopy(current_self)
                    #print("\nWORD BEFORE CALLING APPLY_RULE: ", new_self.current_word.get_word())
                    #print("TERMINAL SUBSTRINGS: ", new_self.get_terminal_substrings())

                    new_self.derivation += new_self.current_word.apply_rule(var, expansion, index)
                    #print(f"\nAPPLYING RULE FROM VAR {var}, EXPANSION {expansion} AT INDEX {index}")

                    #print("\nWORD AFTER CALLING APPLY_RULE: ", new_self.current_word.get_word())

                    if new_self.derivation_complete():
                        return new_self.print_derivation()
                    if new_self.derivation_failed():
                        #print("derivation failed for: ", new_self.current_word)
                        continue
                    elif new_self not in paths.queue:
                        paths.put((new_self.get_priority(), id(new_self), new_self))

        print("Queue empty, word rejected.")
        return


#print(cg1)
#deriv = Derivation(cg1, Word(cg1, 'aaabbbccc'))


#print(deriv.get_derivation())




