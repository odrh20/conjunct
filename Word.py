"""
Class for words in a CYK Parser derivation, used in constructing derivations from a given recognition matrix.
"""
import copy


class Word:

    def __init__(self, grammar, current_word, target_word, variable_tracker=None):
        self.grammar = grammar
        self.current_word = current_word
        self.target_word = target_word

        """
        Variable tracker: an ordered list of (variable, matrix position) pairs which shows where each variable in the
        word is located in the recognition matrix.
        """
        if variable_tracker is None:
            self.variable_tracker = [(self.grammar.start_variable, (0, len(self.target_word) - 1))]

    def __str__(self):
        return self.current_word

    def __eq__(self, other):
        return self.current_word == other.current_word

    def __ne__(self, other):
        return not self.__eq__(other)

    def update_variable_tracker(self, node):
        if self.variable_tracker[0][0] != node.variable:
            print("Error trying to update variable tracker")
            return
        self.variable_tracker.pop(0)
        new_variables = []
        for conjunct, left_pos, right_pos in node.pointers:
            if not (left_pos is None and right_pos is None):
                new_variables.append((conjunct[0], left_pos))
                new_variables.append((conjunct[1], right_pos))
        self.variable_tracker = new_variables + self.variable_tracker

    def get_var_index_pos(self):
        print("current word: ", self.current_word)
        print("variable tracker: ", self.variable_tracker)
        var, pos = self.variable_tracker[0]
        index = self.current_word.find(var)
        return var, index, pos

    def set_word(self, word):
        if len(word) == 0:
            self.current_word = 'e'
        else:
            self.current_word = word

    def replace_word_section(self, new_string, start, end):
        """
        Remove the section of current word between start and end indices, and replace it with new_string.
        """

        new_word = self.current_word[:start] + new_string + self.current_word[end:]
        # Now scan the word, if there are any & symbols directly to the right of a (, then add an 'e' between them
        for i in range(len(new_word)):
            if (new_word[i] == '(' and new_word[i+1] == '&') or (new_word[i] == '&' and new_word[i+1] == ')'):
                new_word = new_word[:i+1] + 'e' + new_word[i+1:]
        self.set_word(new_word)
        return

    def apply_rule(self, variable, expansion, index):
        """
        Replace the variable with the expansion at the given index, where the expansion is a tuple of conjuncts
        eg. Variable = A, Conjuncts = (a1, a2), Index = 1
        xAyA => x(a1 & a2)yA
        """
        self_ = copy.deepcopy(self)
        if self.current_word[index] != variable:
            return "Error. Variable not found at given index in word."

        new_string = "("
        for idx, conjunct in enumerate(expansion):
            if idx > 0:
                new_string += "&"
            if conjunct != 'e':
                new_string += conjunct
        new_string += ")"

        self_.replace_word_section(new_string, index, index+len(variable))
        derivation = [(self_, self_.grammar.print_rule(variable, expansion), [index])]
        reduce_list = self_.reduce_conjuncts()
        if len(reduce_list) > 0:
            derivation += reduce_list
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
        for i in range(len(self.current_word[start:])):
            if self.current_word[start+i] == '(':
                open_bracket = start+i
                for j in range(len(self.current_word[start+i+1:])):
                    if self.current_word[start+j+i+1] == ')':
                        close_bracket = start+j+i+1
                        break
                break

        if open_bracket == -1 or close_bracket == -1:
            # Then we have not found any brackets, so the word does not need to be modified.
            return derivation

        # If we have found brackets, investigate what is inside them.
        self_ = copy.deepcopy(self)
        inside_brackets = self.current_word[open_bracket+1:close_bracket]

        conjuncts = inside_brackets.split('&')

        terminal_conjunct = all(letter in self.grammar.terminals for letter in conjuncts[0])
        if (terminal_conjunct or conjuncts[0] == 'e') and len(set(conjuncts)) == 1:  # Then we need to reduce them
            self_.replace_word_section(conjuncts[0], open_bracket, close_bracket+1)
            derivation.append((self_, "Reduce conjuncts", [open_bracket, close_bracket]))
            return self_.reduce_conjuncts(derivation=derivation)

        # Recursively call function on remainder of string.
        return self_.reduce_conjuncts(start=open_bracket+1, derivation=derivation)