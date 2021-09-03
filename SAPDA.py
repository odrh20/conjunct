"""
Class for SAPDA objects
"""

class SAPDA:
    def __init__(self, states, input_alphabet, stack_alphabet, transitions,
                 initial_state, initial_stack_symbol, name=None, user_defined=False):
        """Instantiate SAPDA object"""


        self.name = name
        self.states = self.set_all_str(states)
        self.input_alphabet = self.set_all_str(input_alphabet)
        self.stack_alphabet = self.set_all_str(stack_alphabet)
        self.transitions = transitions
        self.initial_state = str(initial_state)
        self.initial_stack_symbol = str(initial_stack_symbol)
        self.user_defined = user_defined

    def __eq__(self, other):
        return (self.states == other.states) and (self.input_alphabet == other.input_alphabet) and \
               (self.stack_alphabet == other.stack_alphabet) and (self.transitions == other.transitions) == \
               (self.initial_state == other.initial_state) and (self.initial_stack_symbol == other.initial_stack_symbol)

    def __str__(self):
        sapda_string = f"{self.name}\n"
        sapda_string += "\nStates:\n   {"
        for idx, state in enumerate(sorted(self.states)):
            sapda_string += state
            if idx + 1 < len(sorted(self.states)):
                sapda_string += ", "
            else:
                sapda_string += "}\n"

        sapda_string += "\nInput Alphabet:\n   {"
        for idx, letter in enumerate(sorted(self.input_alphabet)):
            sapda_string += letter
            if idx + 1 < len(sorted(self.input_alphabet)):
                sapda_string += ", "
            else:
                sapda_string += "}\n"

        sapda_string += "\nStack Alphabet:\n   {"
        for idx, letter in enumerate(sorted(self.stack_alphabet)):
            sapda_string += letter
            if idx + 1 < len(sorted(self.stack_alphabet)):
                sapda_string += ", "
            else:
                sapda_string += "}\n"

        sapda_string += "\nInitial State:\n   " + self.initial_state + "\n"
        sapda_string += "\nInitial Stack Symbol:\n   " + self.initial_stack_symbol + "\n"
        sapda_string += self.print_transitions()


        sapda_string += "\nThis is a " + self.deterministic_or_non_deterministic() + " SAPDA."
        return sapda_string

    def print_transitions(self):
        trans_str = "\nTransitions:\n   "
        for idx, transition in enumerate(self.get_transition_list()):
            trans_str += str(idx + 1) + ".  " + transition + "\n   "
        return trans_str

    def deterministic_or_non_deterministic(self):
        """
        For any combination of current state, next input letter, top stack symbol, if there is more than one transition
        available (reading either the next letter or 'e'), then it is non-deterministic.
        Else, it is deterministic.
        """

        for state in self.transitions:
            for pop in self.transitions[state]:
                for letter in self.transitions[state][pop]:
                    if len(self.transitions[state][pop][letter]) > 1:
                        return "non-deterministic"
                    if letter != 'e' and 'e' in self.transitions[state][pop]:
                        return "non-deterministic"
        return "deterministic"

    def get_transition_list(self):
        """
        Returns a list of all transitions in the form δ(state, letter, pop) = ((q1, a1) ^ ... (qk, ak)), ... for
        printing.
        """
        transition_list = []
        for state in self.transitions:
            for pop in self.transitions[state]:
                for letter in self.transitions[state][pop]:
                    transitions = self.transitions[state][pop][letter]
                    transition_list.append(
                        "δ(" + state + ", " + letter + ", " + pop + ") = " + self.denote_transitions(transitions))
        transition_string = ""
        for transition in transition_string:
            transition_string += transition
        return transition_list

    @staticmethod
    def denote_transitions(transitions):
        """
        Take set of transitions of form {((q1, a1), ..., (q2, ak)), ... }
        Return string of transitions in form "{((q1, a1) ^ ... (qk, ak)), ... }"
        """
        trans_string = ""
        for index, transition in enumerate(transitions):
            if index == 0:
               trans_string += "{"
            if index > 0:
                trans_string += ", "
            for idx, (next_state, push) in enumerate(transition):
                if idx > 0:
                    trans_string += " ∧ "
                trans_string += "(" + next_state + ", " + push + ")"
            if index + 1 == len(transitions):
               trans_string += "}"

        return trans_string

    @staticmethod
    def set_all_str(old_set):
        new_set = set()
        for item in old_set:
            new_set.add(str(item))
        return new_set


    def is_valid_transition(self, transition):
        """
        Take user input for transition in the form [state, stack string, state, stack string, ...].
        Check if it is a valid transition.
        """
        if len(transition) % 2 != 0 or len(transition) < 2:
            return False

        else:
            for i in range(len(transition)):
                if i % 2 == 0 and transition[i] not in self.states:
                    return False
                if i % 2 != 0 and not self.is_valid_stack_string(transition[i]):
                    return False

        return True

    def is_valid_stack_string(self, stack_string):
        if stack_string == 'e':
            return True
        for letter in stack_string:
            if letter not in self.stack_alphabet:
                return False
        return True
