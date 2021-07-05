# Class for conjunctive grammar
from prompt_toolkit import print_formatted_text, HTML
from SAPDA import *
from Computation import *


class CG:
    def __init__(self, user=False, name=None, terminals=None, variables=None, start_variable=None, rules=None):
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
        for variable in self.rules:
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

        if ('e', ) in self.rules[self.start_variable]:
            for variable in self.rules:
                for expansion in self.rules[variable]:
                    for conjunct in expansion:
                        for letter in conjunct:
                            if letter == self.start_variable:
                                return False

        for variable in self.rules:
            for expansion in self.rules[variable]:
                if len(expansion) == 1 and expansion[0] in self.terminals:
                    continue
                else:
                    for conjunct in expansion:
                        if len(conjunct) == 2 and conjunct[0] in self.variables and conjunct[1] in self.variables:
                            continue
                        else:
                            return False

        return True


# a^n b^n c^n (n>=0)
cg1 = CG(
    name="Words made of blocks of a's, b's and c's of equal length. {a^n b^n c^n | n > 0}",
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

# wcw w: {a,b} Reduplication with centre marker
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

cg5 = CG(
    terminals={'a'},
    variables={'S', 'A', 'B'},
    start_variable='S',
    rules={
        'S': {('A', 'B')},
        'A': {('e',), ('Aa',)},
        'B': {('e',), ('Ba',)}
    },
)

