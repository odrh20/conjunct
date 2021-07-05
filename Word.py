from CG import *

"""
Class for words in grammar derivations. 
Words are represented by strings made up of terminals and variables from the grammar, as well as the 
special symbols '(', ')', and '&'. 

"""


class Word:

    def __init__(self, grammar, word):
        self.grammar = grammar
        self.word = word

    def __str__(self):
        return self.get_word()

    def __eq__(self, other):
        return self.get_word() == other.get_word()

    def __ne__(self, other):
        return not self.__eq__(other)

    def get_word(self):
        return self.word

    def get_terminal_variable_string(self):
        """
        Returns the word without any characters which are not terminals or variables.
        """
        return_string = ""
        for letter in self.get_word():
            if letter not in {'(', ')', '&', 'e'}:
                return_string += letter
        return return_string

    # def has_invalid_conjuncts(self):
    #     """
    #     Checks the list of conjuncts contained in the word.
    #     """
    #     max_conjuncts = 0
    #     for conjuncts in self.get_conjunct_list():
    #         for conjunct in conjuncts:
    #             if not any(symbol in self.grammar.variables for symbol in conjunct):
    #                 terminal_count = 0
    #                 for symbol in conjunct:
    #                     if symbol in self.grammar.terminals:
    #
    #                 max_conjuncts = len(conjunct)
    #     return max_conjuncts

    def get_terminal_string(self):
        """
        Returns the word with only terminal symbols.
        """
        return_string = ""
        for letter in self.get_word():
            if letter in self.grammar.terminals:
                return_string += letter
        return return_string

    def set_word(self, word):
        if len(word) == 0:
            self.word = 'e'
        else:
            self.word = word

    def has_variables(self):
        """
        As long as there are variables in the word which are in the grammar's rules, return True.
        """
        # for letter in self.word:
        #     if letter in self.grammar.rules:
        #         return True
        return any(letter in self.grammar.rules for letter in self.get_word())
        # return False

    def get_current_variables(self):
        """
        Scans the word to find variables. Return a list of triples of (variable, word, variable index).
        """
        variables = []
        for i in range(len(self.word)):
            if self.word[i] in self.grammar.rules:
                variables.append((self.word[i], self.word, i))
        return variables

    def get_conjunct_list(self):
        """
        Returns a 2D list containing all lists of conjuncts within brackets in the word.
        Scan the word to match each left bracket with its corresponding right bracket and get the substring within.
        Then split it by & to get the local list of conjuncts, and append this list to the main list.
        eg. ((Aa)&B) returns [ [(Aa), B] , [Aa] ]
        """

        conjunct_list = []
        open_count = 0
        count_list = []

        for symbol in self.get_word():
            if symbol == '(':
                open_count += 1
                count_list.append(open_count)
            elif symbol == ')':
                open_count -= 1
                count_list.append(open_count)
            else:
                count_list.append(-1)

        for i in range(len(self.get_word())):
            if self.get_word()[i] == '(':
                for j in range(i+1, len(self.get_word())):
                    if count_list[j] == count_list[i] - 1:  # Then get substring between index i and j
                        substring = self.get_word()[i+1:j]
                        local_conjuncts = substring.split('&')
                        conjunct_list.append(local_conjuncts)
                        break

        return conjunct_list

    def replace_word_section(self, new_string, start, end):
        """
        Remove the section of current word between start and end indices, and replace it with new_string.
        """

        new_word = self.get_word()[:start] + new_string + self.get_word()[end:]
        # Now scan the word, if there are any & symbols directly to the right of a (, then add an 'e' between them
        for i in range(len(new_word)):
            if (new_word[i] == '(' and new_word[i+1] == '&') or (new_word[i] == '&' and new_word[i+1] == ')'):
                #print(f"\nNEED TO ADD AN e for word: {new_word}\n")
                new_word = new_word[:i+1] + 'e' + new_word[i+1:]
        self.set_word(new_word)
        return

    def apply_rule(self, variable, expansion, index):
        """
        Replace the variable with the expansion at the given index, where the expansion is a tuple of conjuncts
        eg. Variable = A, Conjuncts = (a1, a2), Index = 1
        xAyA => x(a1 & a2)yA
        """
        if self.word[index] != variable:
            return "Error. Variable not found at given index in word."

        new_string = "("
        for idx, conjunct in enumerate(expansion):
            if idx > 0:
                new_string += "&"
            if conjunct != 'e':
                new_string += conjunct
        new_string += ")"

        self.replace_word_section(new_string, index, index+1)
        #print(self.get_conjunct_list())
        derivation = [(self.get_word(), self.grammar.print_rule(variable, expansion), [index])]
        reduce_list = self.reduce_conjuncts()
        #print(self.get_conjunct_list())
        if len(reduce_list) > 0:
            #print("REDUCTION OCCURRED")
            derivation += reduce_list
        #else:
            #print("NO REDUCTION")
        return derivation

    def reduce_conjuncts(self, start=0, derivation=None):
        """
        Scan the word to find any occurrences of (x & ... & x) where x is a string made of terminals.
        Replace this entire part with a single string x without brackets.
        eg. AB(a & a)C => ABaC
            b(c)a => bca
        """

        if derivation is None:
            derivation = []
        open_bracket = -1
        close_bracket = -1
        for i in range(len(self.word[start:])):
            if self.word[start+i] == '(':
                open_bracket = start+i
                for j in range(len(self.word[start+i+1:])):
                    if self.word[start+j+i+1] == ')':
                        close_bracket = start+j+i+1
                        break
                break

        if open_bracket == -1 or close_bracket == -1:
            # Then we have not found any brackets, so the word does not need to be modified.
            return derivation

        # If we have found brackets, investigate what is inside them.
        inside_brackets = self.word[open_bracket+1:close_bracket]

        conjuncts = inside_brackets.split('&')

        terminal_conjunct = all(letter in self.grammar.terminals for letter in conjuncts[0])
        if (terminal_conjunct or conjuncts[0] == 'e') and len(set(conjuncts)) == 1:  # Then we need to reduce them

            self.replace_word_section(conjuncts[0], open_bracket, close_bracket+1)
            derivation.append((self.get_word(), "Reduce conjuncts", [open_bracket, close_bracket]))
            return self.reduce_conjuncts(derivation=derivation)

        # Recursively call function on remainder of string.
        return self.reduce_conjuncts(start=open_bracket+1, derivation=derivation)




#start_word = Word(cg1, '(abcab&(abcab&a(bcab&b(c(a(b()))))))')
#print("Before: ", start_word)

#print(start_word.reduce_conjuncts())
#print("After: ", start_word)

# test_word = Word(cg1, 'S')
# print("word before: ", test_word)
# print(test_word.apply_rule('S', ('A', 'B'), 0))
#
# print("word after: ", test_word)
# print(test_word.apply_rule('B', ('bbc',), 3))
# print("word after: ", test_word)

