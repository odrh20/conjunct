# Class for conjunctive grammar
from prompt_toolkit import print_formatted_text, HTML
from SAPDA import *
from Computation import *
from itertools import chain, combinations



class CG:
    def __init__(self, user=False, name=None, terminals=None, variables=None, start_variable=None, rules=None,
                 chars=None):
        """Instantiate Conjunctive Grammar object"""

        if user:
            self.name = self.name_CG()
            self.start_variable, self.variables = self.set_variables()
            self.terminals = self.set_terminals()
            self.rules = dict()
            self.rules = self.add_rules()

        else:
            self.name = name
            self.variables = self.set_all_str(variables)
            self.terminals = self.set_all_str(terminals)
            self.rules = rules
            self.start_variable = str(start_variable)

        if chars is None:
            #char_string = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!"#$%*+,-./:;<=>?@[]^_`{}~'
            upper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            lower = 'abcdefghijklmnopqrstuvwxyz'
            self.chars = []
            for char in upper:
                self.chars.append(char)
            for i in range(1000, 2000):
                if chr(i) not in (upper+lower):
                    self.chars.append(chr(i))

    def __eq__(self, other):
        return (self.terminals == other.terminals) and (self.variables == other.variables) and \
               (self.start_variable == other.start_variable) and (self.rules == other.rules)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        CG_string = f"{self.name}\n"
        CG_string += "\nTerminals:\n   {"
        for idx, terminal in enumerate(sorted(self.terminals)):
            CG_string += terminal
            if idx + 1 < len(sorted(self.terminals)):
                CG_string += ", "
            else:
                CG_string += "}\n"

        CG_string += "\nVariables:\n   {"
        for idx, letter in enumerate(sorted(self.variables)):
            CG_string += letter
            if idx + 1 < len(sorted(self.variables)):
                CG_string += ", "
            else:
                CG_string += "}\n"

        CG_string += f"\nStart Variable:\n   {self.start_variable}\n"
        CG_string += self.print_rules()

        return CG_string

    def generate_new_variable(self):

        for i in range(len(self.chars)):
            if self.chars[i] not in self.variables.union(self.terminals):
                self.variables.add(self.chars[i])
                return self.chars.pop(i)

        print("Ran out of chars for new variables!")
        return ""

    @staticmethod
    def name_CG():
        return input("\nEnter a name for your Conjunctive Grammar: ")

    @staticmethod
    def set_variables():
        print_formatted_text(HTML('<u>\nVARIABLES\n</u>'))
        print("Input all variables separated by spaces. The first variable will be taken as the start variable.\n")
        variables = input("Enter variables: ").split()
        return str(variables[0]), set(variables)

    @staticmethod
    def set_terminals():
        print_formatted_text(HTML('<u>\nTERMINALS\n</u>'))
        print("Input all terminal symbols separated by spaces.\n")
        input_alphabet = input("Enter terminals: ").split()
        return set(input_alphabet)

    def add_rules(self):
        """
        Prompt user to add all rules for each variable.
        """

        if bool(self.rules):
            print(self.print_rules())

        print_formatted_text(HTML('<u>\nRULES\n</u>'))
        rule_LHS = input("Enter a variable for the left-hand side of the rule:  ")

        if not rule_LHS:
            print("\nConjunctive Grammar created!\n")
            return self.rules

        if rule_LHS not in self.variables:
            print("\nNot a variable. Try again.\n")
            return self.add_rules()

        variable = rule_LHS

        rule_RHS = input("\nEnter conjuncts for the right-hand side of rule, separated by spaces:  ").split()

        if not self.is_valid_expansion(rule_RHS):
            print("\nInvalid expansion. Try again.\n")
            return self.add_rules()

        expansion = tuple(rule_RHS)

        if variable not in self.rules:
            self.rules[variable] = set()

        self.rules[variable].add(expansion)
        return self.add_rules()

    def is_valid_expansion(self, expansion):
        """
        Take user input for conjuncts on RHS of rule in the form [expansion 1, expansion 2, ...].
        Check if all are valid expansions.
        """
        if len(expansion) == 0:
            return False

        for conjunct in expansion:
            if len(conjunct) == 1:
                if conjunct == 'e' or conjunct in self.variables or conjunct in self.terminals:
                    continue
                else:
                    return False
            if len(conjunct) > 1:
                for symbol in conjunct:
                    if symbol in self.variables or symbol in self.terminals:
                        continue
                    else:
                        return False
        return True

    @staticmethod
    def set_all_str(old_set):
        new_set = set()
        for item in old_set:
            new_set.add(str(item))
        return new_set

    def order_expansions(self, expansions):
        ordered_list = []
        for expansion in expansions:
            if len(expansion) > 1:
                ordered_list.append(expansion)
        for expansion in expansions:
            if expansion not in ordered_list and len(expansion[0]) > 1:
                ordered_list.append(expansion)
        for expansion in expansions:
            if expansion not in ordered_list and expansion[0] in self.variables:
                ordered_list.append(expansion)
        for expansion in expansions:
            if expansion not in ordered_list and expansion[0] in self.terminals:
                ordered_list.append(expansion)
        for expansion in expansions:
            if expansion not in ordered_list and expansion[0] == 'e':
                ordered_list.append(expansion)
        return ordered_list

    def print_rules(self):
        rule_list = []
        variable_list = [self.start_variable]
        for variable in self.rules:
            if variable not in variable_list:
                variable_list.append(variable)
        for variable in variable_list:
            rule_string = variable + "  ⟶   "
            for index, rule in enumerate(self.order_expansions(self.rules[variable])):
                if index > 0:
                    rule_string += " | "
                for idx, expansion in enumerate(rule):
                    if idx > 0:
                        rule_string += " & "
                    rule_string += expansion

            rule_list.append(rule_string)

        rules_str = "\nRules:\n   "
        for idx, rule in enumerate(rule_list):
            rules_str += str(idx + 1) + ".  " + rule + "\n   "
        return rules_str

    @staticmethod
    def print_rule(variable, expansion):
        rule_string = variable + "  ⟶   "
        for idx, conjunct in enumerate(expansion):
            if idx > 0:
                rule_string += " & "
            rule_string += conjunct
        return rule_string

    def convert_to_sapda(self):
        """
        Return an equivalent single-state SAPDA object by following the conversion algorithm.
        For each terminal symbol a, create transition δ(q, a, a) = (q, e)
        For each rule A -> a1 & ... & ak, create transition δ(q, e, A) = (q, a1) ∧ ... ∧ (q, ak)
        """
        transitions = dict()
        transitions['q'] = dict()

        for variable in self.rules:
            if variable not in transitions['q']:
                transitions['q'][variable] = dict()
            if 'e' not in transitions['q'][variable]:
                transitions['q'][variable]['e'] = set()
            for expansion in self.rules[variable]:
                transition_list = []
                for conjunct in expansion:
                    transition_list.append(('q', conjunct))
                transitions['q'][variable]['e'].add(tuple(transition_list))

        for terminal in self.terminals:
            transitions['q'][terminal] = dict()
            transitions['q'][terminal][terminal] = {(('q', 'e'),)}

        return SAPDA(
            name=f"SAPDA converted from {self.name}",
            states={'q'},
            input_alphabet=self.terminals,
            stack_alphabet=self.variables.union(self.terminals),
            transitions=transitions,
            initial_state='q',
            initial_stack_symbol=self.start_variable
            )

    def is_in_BNF(self):
        """
        Checks if the grammar is in Binary Normal Form.
        A grammar is in BNF if each rule is in one of the following forms:
        1) A -> B1C1 & ... & BmCm where m >= 1 and A, Bi, Ci are variables
        2) A -> a (to a single terminal symbol)
        3) S -> e if S does not appear on the right-hand side of any rules in R
        """

        # Check if start variable appears on the RHS of any rules
        S_on_RHS = False
        for variable in self.rules:
            for expansion in self.rules[variable]:
                for conjunct in expansion:
                    for letter in conjunct:
                        if letter == self.start_variable:
                            S_on_RHS = True

        for variable in self.rules:
            for expansion in self.rules[variable]:
                if variable == self.start_variable and expansion == ('e',) and not S_on_RHS:
                    continue
                elif len(expansion) == 1 and expansion[0] in self.terminals:
                    continue
                else:
                    for conjunct in expansion:
                        if len(conjunct) == 2 and conjunct[0] in self.variables and conjunct[1] in self.variables:
                            continue
                        else:
                            print("Conjunct: ", conjunct)
                            print("Expansion: ", expansion)
                            print("Variable: ", variable)
                            return False

        return True

    def get_nullable_set(self):
        """
        Return set of all variables in the grammar which can generate the empty word.
        """
        nullable = set()
        for variable in self.rules:
            for expansion in self.rules[variable]:
                if expansion == ('e',):
                    nullable.add(variable)
                    break

        for variable in self.rules:
            if variable not in nullable:
                for expansion in self.rules[variable]:
                    if len(expansion) == 1 and expansion[0] in nullable:
                        nullable.add(variable)
                        break

        for variable in self.rules:
            if variable not in nullable:
                for expansion in self.rules[variable]:
                    to_add = True
                    for conjunct in expansion:
                        for letter in conjunct:
                            if letter not in nullable:
                                to_add = False
                    if to_add:
                        nullable.add(variable)
                        break
        return nullable

    def get_null_expansions(self, expansion):
        """
        Return a list of expansions formed from all possible combinations of removing nullable variables from a given
        expansion.
        Generate a list of all indices where a nullable variable appears in the expansion, then generate a power set
        from this.
        For each index list in the power set, create a new expansion where the variable at each index is removed.
        If all characters are removed from a conjunct in the expansion, change the conjunct to 'e' for the empty word.
        """
        nullable_indices = []
        for i in range(len(expansion)):
            for j in range(len(expansion[i])):
                if expansion[i][j] in self.get_nullable_set():
                    nullable_indices.append([i, j])
        index_powerset = list(chain.from_iterable(combinations(nullable_indices, k)
                                                  for k in range(1, len(nullable_indices) + 1)))
        new_expansions = []
        for indices in index_powerset:
            new_expansion = []
            for i in range(len(expansion)):
                new_conjunct = ''
                for j in range(len(expansion[i])):
                    if [i, j] not in indices:
                        new_conjunct += expansion[i][j]
                if len(new_conjunct) == 0:
                    new_conjunct = 'e'
                new_expansion.append(new_conjunct)
            new_expansions.append(tuple(new_expansion))
        return new_expansions

    def remove_e_conjuncts(self):
        """
        For each rule in the grammar, add new rules where nullable variables are removed in all combinations.
        Then, remove any rule containing an e-conjunct.
        """

        for variable in self.rules:
            expansion_list = list(self.rules[variable])
            for expansion in expansion_list:
                for new_expansion in self.get_null_expansions(expansion):
                    self.rules[variable].add(new_expansion)

        for variable in self.rules:
            expansion_list = list(self.rules[variable])
            for expansion in expansion_list:
                for conjunct in expansion:
                    if conjunct == 'e':
                        self.rules[variable].remove(expansion)
                        break
        return

    def get_unit_conjuncts(self):
        """
        Return a list of all rules in the grammar containing a unit conjunct.
        (ie. of the form A -> a1 & ... & a(k-1) & ... & B & a(k+1) & ... & am)

        List contains pairs of (variable, expansion, [unit indices]).
        """
        unit_conjuncts = []
        for variable in self.rules:
            for expansion in self.rules[variable]:
                for i in range(len(expansion)):
                    if expansion[i] in self.variables:
                        unit_conjuncts.append((variable, expansion, expansion[i], i))

        return unit_conjuncts

    def remove_unit_conjuncts(self):
        """
        While list of unit conjuncts is not empty:
            For each unit conjunct:
                Delete its rule, and add new rules where the unit conjunct is replaced by all its expansions
        """
        while len(self.get_unit_conjuncts()) > 0:
            variable, expansion, conjunct, index = self.get_unit_conjuncts().pop(0)
            self.rules[variable].remove(expansion)
            if variable not in expansion:
                for c_expansion in self.rules[conjunct]:
                    # Create a new rule from variable to
                    new_rule = []
                    for c in range(len(expansion)):
                        if c == index:
                            for c_conj in c_expansion:
                                new_rule.append(c_conj)
                        else:
                            new_rule.append(expansion[c])
                    self.rules[variable].add(tuple(new_rule))
        return

    def collapse_equal_conjuncts(self):
        """
        Remove any duplicate conjuncts in all the rules.
        """
        for variable in self.rules:
            for expansion in self.rules[variable]:
                if len(expansion) > 1:
                    self.rules[variable].remove(expansion)
                    self.rules[variable].add(tuple(set(expansion)))



    def remove_useless_rules(self):
        """
        All conjuncts either have:
            Type 1: A -> a (a single terminal)
            Type 2: A -> X, where X is a string of terminals/variables of length at least 2
        Delete any rule which has conjuncts of both type
        Any rule A -> a
        Then delete any rule that has more than one conjunct consisting of only terminals
        """
        for variable in self.rules:
            expansion_list = list(self.rules[variable])
            for expansion in expansion_list:
                has_type_1 = False
                has_type_2 = False
                terminal_conjuncts = 0
                for conjunct in expansion:
                    if conjunct in self.terminals:
                        has_type_1 = True
                    else:
                        has_type_2 = True
                    if all(symbol in self.terminals for symbol in conjunct):
                        terminal_conjuncts += 1
                if (has_type_1 and has_type_2) or terminal_conjuncts > 1:
                    self.rules[variable].remove(expansion)
        return

    def terminals_to_variables(self):
        """
        For any terminal found in a rule expansion, create a new variable with a single rule to the terminal.
        """
        found_terminals = []
        rules_to_change = []
        for variable in self.rules:
            for expansion in self.rules[variable]:
                if not (len(expansion) == 1 and expansion[0] in self.terminals):
                    for conjunct in expansion:
                        for symbol in conjunct:
                            if symbol in self.terminals:
                                if symbol not in found_terminals:
                                    found_terminals.append(symbol)
                                if (variable, expansion) not in rules_to_change:
                                    rules_to_change.append((variable, expansion))

        new_rules = dict()
        for terminal in found_terminals:
            new_var = self.generate_new_variable()
            self.rules[new_var] = {(terminal,)}
            new_rules[terminal] = new_var

        for variable, expansion in rules_to_change:
            self.rules[variable].remove(expansion)
            new_exp = []
            for conjunct in expansion:
                new_conjunct = ''
                for i in range(len(conjunct)):
                    if conjunct[i] in new_rules:
                        new_conjunct += new_rules[conjunct[i]]
                    else:
                        new_conjunct += conjunct[i]
                new_exp.append(new_conjunct)
            self.rules[variable].add(tuple(new_exp))
        return

    def get_long_conjuncts(self):
        long_conjuncts = []
        for variable in self.rules:
            for expansion in self.rules[variable]:
                for conjunct in expansion:
                    if len(conjunct) > 2 and (variable, expansion) not in long_conjuncts:
                        long_conjuncts.append((variable, expansion))
        return long_conjuncts

    def split_long_conjuncts(self):

        new_rules = dict()
        while len(self.get_long_conjuncts()) > 0:
            for variable, expansion in self.get_long_conjuncts():
                self.rules[variable].remove(expansion)
                new_exp = []
                for conjunct in expansion:
                    if len(conjunct) > 2:
                        if conjunct[0:2] not in new_rules:
                            new_rules[conjunct[0:2]] = self.generate_new_variable()
                        new_conj = new_rules[conjunct[0:2]] + conjunct[2:]
                    else:
                        new_conj = conjunct
                    new_exp.append(new_conj)
                self.rules[variable].add(tuple(new_exp))

        for exp, var in new_rules.items():
            self.rules[var] = {(exp,)}
        return

    def convert_to_BNF(self):

        e_in_language = False
        if self.start_variable in self.get_nullable_set():
            e_in_language = True

        #print("e in language: ", e_in_language)
        print(self)
        #print("REMOVING E CONJUNCTS")
        self.remove_e_conjuncts()
        #print(self)
        #print("REMOVING UNIT CONJUNCTS")
        #print(self.get_unit_conjuncts())
        self.remove_unit_conjuncts()
        #print(self)
        self.collapse_equal_conjuncts()
        #print("REMOVING USELESS RULES")
        self.remove_useless_rules()
        #print(self)
        #print("TERMINALS TO VARIABLES")
        self.terminals_to_variables()
        #print(self)
        #print("SPLIT LONG CONJUNCTS")
        self.split_long_conjuncts()
        #print(self)

        if e_in_language:
            old_start_var = self.start_variable
            new_start_var = self.generate_new_variable()
            self.start_variable = new_start_var
            self.rules[new_start_var] = {('e',)}
            for exp in self.rules[old_start_var]:
                self.rules[new_start_var].add(exp)
            #print(self)
        print("\nCONVERTING TO BINARY NORMAL FORM\n")
        print(self)
        return













# a^n b^n c^n (n>=0)
cg1 = CG(
    name="Words made of blocks of a's, b's and c's of equal length. {a^n b^n c^n | n >= 0}",
    terminals={'a', 'b', 'c'},
    variables={'S', 'A', 'B', 'C', 'D'},
    start_variable='S',
    rules={
        'S': {('A', 'C'), ('e', )},
        'A': {('aA', ), ('B', )},
        'B': {('bBc', ), ('e', )},
        'C': {('Cc', ), ('D', )},
        'D': {('aDb', ), ('e', )},
    },
)

cg2 = CG(
    name="Cross agreement language: a^m b^n c^m d^n (n>=0)",
    terminals={'a', 'b', 'c', 'd'},
    variables={'S', 'A', 'B', 'C', 'D', 'X', 'Y'},
    start_variable='S',
    rules={
        'S': {('XD', 'AY')},
        'A': {('aA', ), ('e', )},
        'B': {('bB', ), ('e', )},
        'C': {('cC', ), ('e', )},
        'D': {('dD', ), ('e', )},
        'X': {('aXc', ), ('B', )},
        'Y': {('bYd', ), ('C', )},
    },
)

# w$w w: {a,b} Reduplication with centre marker
cg3 = CG(
    name="Reduplication with centre marker: {w$w | w ∈ {a, b}*}",
    terminals={'a', 'b', '$'},
    variables={'S', 'A', 'B', 'C', 'D', 'E'},
    start_variable='S',
    rules={
        'S': {('C', 'D')},
        'C': {('aCa', ), ('aCb', ), ('bCa', ), ('bCb', ), ('$',)},
        'D': {('aA', 'aD'), ('bB', 'bD'), ('$E',)},
        'A': {('aAa', ), ('aAb', ), ('bAa', ), ('bAb', ), ('$Ea', )},
        'B': {('aBa', ), ('aBb', ), ('bBa', ), ('bBb', ), ('$Eb', )},
        'E': {('aE', ), ('bE', ), ('e', )},
    },
)

#
cg4 = CG(
    terminals={'a', 'b'},
    variables={'S'},
    start_variable='S',
    rules={
        'S': {('aSa',), ('aSb',), ('e', )},
    },
)

# Just for testing
cg5 = CG(
    terminals={'a', 'b'},
    variables={'S', 'A', 'B'},
    start_variable='S',
    rules={
        'S': {('AB',), ('e',)},
        'A': {('a',)},
        'B': {('b',)}
    },
)

cg6 = CG(
    terminals={'a'},
    variables={'A', 'B', 'C', 'D'},
    start_variable='A',
    rules={
        'A': {('AC', 'BB'), ('a',)},
        'B': {('AA', 'BD'), ('aa',)},
        'C': {('AB', 'DD'), ('aaa',)},
        'D': {('AB', 'CC')}
    },
)


# print(cg4.is_in_BNF())
# cg4.convert_to_BNF()
# print(cg4.is_in_BNF())
#
# print(cg1.chars)

print(cg6)

print(cg6.convert_to_BNF())