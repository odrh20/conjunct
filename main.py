from kivy.app import App
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, NumericProperty, ListProperty
from kivy.properties import StringProperty
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput, FL_IS_LINEBREAK
from kivy.metrics import sp
from kivy.graphics import *
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')


from CG import *
from SAPDA import *
from Parser import *

import re

file = open("instructions.txt")


# Define the different screens

class StartWindow(Screen):
    pass


class GettingStartedWindow(Screen):
    pass

class CGWindow(Screen):
    pass


class SAPDAWindow(Screen):
    pass


class ChooseCGWindow(Screen):
    pass


class ChooseSAPDAWindow(Screen):
    pass


class CGTutorialWindow(Screen):
    pass


class SAPDATutorialWindow(Screen):
    pass


class MakeCGWindow(Screen):
    pass


class MakeSAPDAWindow(Screen):
    pass


class ChooseCGActionWindow(Screen):
    pass


class ChooseSAPDAActionWindow(Screen):
    pass


class CYKParseWindow(Screen):
    pass


class GenerateParseWindow(Screen):
    pass


class ConvertCGToSAPDAWindow(Screen):
    pass


class WindowManager(ScreenManager):
    pass


class SAPDATextInput(TextInput):

    # δ(state, letter, pop) = (next state, push)
    # pattern: δ(□,□,□)=(□,□)

    def insert_text(self, substring, from_undo=False):
        if all(ch == ' ' for ch in super(SAPDATextInput, self).text):
            super(SAPDATextInput, self).text == ''

        s = substring

        super(SAPDATextInput, self).insert_text(s, from_undo=from_undo)
        if s[-1] == "\n":
            super(SAPDATextInput, self).insert_text("δ(□, □, □) = (□, □)", from_undo=from_undo)

    def get_transitions(self, text):

        transitions = [item.replace(" ", "") for item in text.splitlines()]
        for transition in transitions:
            if transition == "":
                transitions.remove(transition)
        return transitions


    def make_user_sapda(self, text):
        """
        Take user input to create a dictionary of SAPDA transitions.
        transitions: a list of strings which each match the pattern
        "δ\(.+,.+,.+\)=(\(.+,.+\)∧)*\(.+,.+\)"
        """

        transitions_list = self.get_transitions(text)

        initial_state = re.search("δ\((.+),.+,.\)=.*", transitions_list[0]).groups()[0]
        initial_stack_symbol = re.search("δ\(.+,.+,(.)\)=.*", transitions_list[0]).groups()[0]

        trans_dict = {}
        states = set()
        input_alphabet = set()
        stack_alphabet = set()

        for transition in transitions_list:

            state = re.search("δ\((.+),.+,.\)=.*", transition).groups()[0]
            states.add(state)
            letter = re.search("δ\(.+,(.+),.\)=.*", transition).groups()[0]
            if letter != 'e':
                input_alphabet.add(letter)
            pop = re.search("δ\(.+,.+,(.)\)=.*", transition).groups()[0]
            stack_alphabet.add(pop)

            if state not in trans_dict:
                trans_dict[state] = {}
            if pop not in trans_dict[state]:
                trans_dict[state][pop] = {}
            if letter not in trans_dict[state][pop]:
                trans_dict[state][pop][letter] = set()

            expansion_str = re.search("δ\(.+,.+,.\)=(.*)", transition).groups()[0]
            expansion_str_list = expansion_str.split("∧")

            expansion = []
            for conjunct_str in expansion_str_list:
                next_state = re.search("\((.+),.+\)", conjunct_str).groups()[0]
                states.add(next_state)
                push_string = re.search("\(.+,(.+)\)", conjunct_str).groups()[0]
                for symbol in push_string:
                    if symbol != 'e':
                        stack_alphabet.add(symbol)
                expansion.append((next_state, push_string))
            trans_dict[state][pop][letter].add(tuple(expansion))

        return SAPDA(name="User SAPDA", states=states, input_alphabet=input_alphabet, stack_alphabet=stack_alphabet,
        transitions=trans_dict, initial_state=initial_state, initial_stack_symbol=initial_stack_symbol, user_defined=True)



    def is_valid_sapda_input(self, text):

        transitions = self.get_transitions(text)
        print("all transitions: ", transitions)
        pattern = re.compile("δ\(.+,.+,.\)=(\(.+,.+\)∧)*\(.+,.+\)")

        return all(pattern.fullmatch(transition) for transition in transitions)




class CGTextInput(TextInput):

    def need_arrow(self):
        text_split = super(CGTextInput, self).text.splitlines()
        #print("text split: ", text_split)
        #print("Need arrow: ", len(text_split) > 0 and len(text_split[-1]) == 1)
        return len(text_split) > 0 and len(text_split[-1]) == 1

    def insert_text(self, substring, from_undo=False):
        if all(ch == ' ' for ch in super(CGTextInput, self).text):
            super(CGTextInput, self).text == ''

        s = substring
        super(CGTextInput, self).insert_text(s, from_undo=from_undo)
        if self.need_arrow():
            super(CGTextInput, self).insert_text(" ⟶ ", from_undo=from_undo)


    def is_valid_cg_input(self, text):
        """
        Checks whether the rules inside the text box are in the right format.
        Each line should consist of a single character, an arrow, and a string,
        ignoring spaces and brackets. eg. S ⟶ ab
        """
        print("CALLING IS_VALID_INPUT (CG)")
        rules = self.get_rules(text)
        return len(rules) > 0 and all(len(rule) > 2 and rule[1] == '⟶' for rule in rules)

    def get_rules(self, text):

        rules = [item.replace(" ", "").replace("(", "").replace(")", "") for item in text.splitlines()]
        for rule in rules:
            if rule == "":
                rules.remove(rule)
        return rules


    def make_user_cg(self, text):
        """
        Take rules as typed by user inside the text box to create a CG object.
        """

        rules = self.get_rules(text)
        print("rules: ", rules)
        var_exp = []
        for item in rules:
            var_exp.append(item.split('⟶'))

        var_conj = []
        for var, exp in var_exp:
            var_conj.append((var,tuple(exp.split('&'))))

        # Get start variable from first rule inputted
        start_variable = var_conj[0][0]

        # Get set of variables from LHS of rules
        variables = set()
        for var, _ in var_conj:
            variables.add(var)

        # Get set of terminals from RHS of rules
        terminals = set()
        for _, conjuncts in var_conj:
            for conjunct in conjuncts:
                for symbol in conjunct:
                    if symbol not in variables.union({'e'}):
                        terminals.add(symbol)

        # Get rule dictionary
        rules = {}
        for var, conjuncts in var_conj:
            if var not in rules:
                rules[var] = set()
            rules[var].add(conjuncts)


        return CG(name="User CG", terminals=terminals, variables=variables, start_variable=start_variable, rules=rules, user_defined=True)





class ConjunctApp(App):

    my_cg = ObjectProperty(None)
    my_bnf_cg = ObjectProperty(None)
    my_parser = ObjectProperty(None)
    my_derivation = ListProperty(None)
    input_string = StringProperty(None)

    my_sapda = ObjectProperty(None)
    my_computation = ListProperty(None)

    cg1 = ObjectProperty(cg1)
    cg2 = ObjectProperty(cg2)
    cg3 = ObjectProperty(cg3)
    cg4 = ObjectProperty(cg4)
    sapda1 = ObjectProperty(sapda1)
    sapda2 = ObjectProperty(sapda2)
    sapda3 = ObjectProperty(sapda3)

    instructions = file.read().split('£')
    getting_started_txt = StringProperty(instructions[0])
    make_cg_txt = StringProperty(instructions[1])
    make_sapda_txt = StringProperty(instructions[2])
    cg_tutorial_txt_1 = StringProperty(instructions[3])
    cg_tutorial_txt_2 = StringProperty(instructions[4])
    cg_tutorial_txt_3 = StringProperty(instructions[5])
    cg_tutorial_txt_4 = StringProperty(instructions[6])
    sapda_tutorial_txt_1 = StringProperty(instructions[7])
    sapda_tutorial_txt_2 = StringProperty(instructions[8])
    sapda_tutorial_txt_3 = StringProperty(instructions[9])
    sapda_tutorial_txt_4 = StringProperty(instructions[10])




    def build(self):

        kv = Builder.load_file('gui.kv')

        return kv


if __name__ == '__main__':

    ConjunctApp().run()
