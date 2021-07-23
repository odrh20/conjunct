from prompt_toolkit import print_formatted_text, HTML


class SAPDA:
    def __init__(self, user=False, name=None, states=None, input_alphabet=None, stack_alphabet=None, transitions=None,
                 initial_state=None, initial_stack_symbol=None):
        """Instantiate SAPDA object"""

        if user:
            self.name_sapda()
            self.set_states()
            self.set_input_alphabet()
            self.set_stack_alphabet()
            self.transitions = dict()
            self.add_transitions()

        else:
            self.name = name
            self.states = self.set_all_str(states)
            self.input_alphabet = self.set_all_str(input_alphabet)
            self.stack_alphabet = self.set_all_str(stack_alphabet)
            self.transitions = transitions
            self.initial_state = str(initial_state)
            self.initial_stack_symbol = str(initial_stack_symbol)

    def __eq__(self, other):
        return (self.states == other.states) and (self.input_alphabet == other.input_alphabet) and \
               (self.stack_alphabet == other.stack_alphabet) and (self.transitions == other.transitions) == \
               (self.initial_state == other.initial_state) and (self.initial_stack_symbol == other.initial_stack_symbol)

    def __ne__(self, other):
        return not self.__eq__(other)

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

        # sapda_string += "\nTransitions:\n   "
        # for idx, transition in enumerate(self.get_transition_list()):
        #     sapda_string += str(idx + 1) + ".  " + transition + "\n   "

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
        print(transition_string)
        return transition_list

    @staticmethod
    def denote_transitions(transitions):
        """
        Take set of transitions of form {((q1, a1), ..., (q2, ak)), ... }
        Return string of transitions in form "{((q1, a1) ^ ... (qk, ak)), ... }"
        """
        trans_string = ""
        for index, transition in enumerate(transitions):
            # if index == 0:
            #    trans_string += "{"
            if index > 0:
                trans_string += ", "
            for idx, (next_state, push) in enumerate(transition):
                if idx > 0:
                    trans_string += " ∧ "
                trans_string += "(" + next_state + ", " + push + ")"
            # if index + 1 == len(transitions):
            #    trans_string += "}"

        return trans_string

    @staticmethod
    def set_all_str(old_set):
        new_set = set()
        for item in old_set:
            new_set.add(str(item))
        return new_set

    # def are_loop_transitions(self):
    #     for state in self.transitions:
    #         print("state: ", state)
    #         for pop_stack in self.transitions[state]:
    #             for read_letter in self.transitions[state][pop_stack]:
    #                 if read_letter == 'e':
    #                     for transition in self.transitions[state][pop_stack][read_letter]:
    #                         print("transition: ", self.transitions[state][pop_stack][read_letter])
    #                         for next_state, push_string in transition:
    #                             if pop_stack == push_string[0]:
    #                                 return True
    #     return False

    def name_sapda(self):
        self.name = input("\nEnter a name for your SAPDA: ")
        return

    def set_states(self):
        print_formatted_text(HTML('<u>\nSTATES\n</u>'))
        print("Input all states separated by spaces. The first state will be taken as the initial state.\n")
        states = input("Enter states: ").split()
        self.initial_state, self.states = str(states[0]), set(states)

    def set_input_alphabet(self):
        print_formatted_text(HTML('<u>\nINPUT ALPHABET\n</u>'))
        print("Input all letters in the input alphabet separated by spaces.\n")
        input_alphabet = input("Enter input alphabet: ").split()
        self.input_alphabet = set(input_alphabet)

    def set_stack_alphabet(self):
        print_formatted_text(HTML('<u>\nSTACK ALPHABET\n</u>'))
        print("Input all letters in the stack alphabet separated by spaces. The first letter will be taken as the "
              "initial stack symbol.\n")
        stack_alphabet = input("Enter stack alphabet: ").split()
        self.initial_stack_symbol, self.stack_alphabet = str(stack_alphabet[0]), set(stack_alphabet)

    def add_transitions(self):
        """
        Prompt user to add all transitions for a given current state, letter to read, and symbol to pop.
        Return a set of transitions of the form {((q1, a1), (q2, a2), ... ), ((q1', a1'), (q2', a2'), ... ), ... }
        """

        if bool(self.transitions):
            print(self.print_transitions())

        print_formatted_text(HTML('<u>\nTRANSITIONS\n</u>'))
        trans_LHS = input("Enter state, letter to read, stack symbol to pop, separated by spaces:  ").split()

        if not trans_LHS:
            print("\nSAPDA created!\n")
            return self.transitions

        if len(trans_LHS) != 3 or trans_LHS[0] not in self.states or trans_LHS[1] not in self.input_alphabet.union({'e'}) \
                or trans_LHS[2] not in self.stack_alphabet:
            print("\nInvalid input. Try again.\n")
            return self.add_transitions()

        state, letter, pop = trans_LHS[0], trans_LHS[1], trans_LHS[2]

        trans_RHS = input("\nEnter conjuncts of next state, stack string to push, separated by spaces:  ").split()

        if not self.is_valid_transition(trans_RHS):
            print("\nInvalid transition. Try again.\n")
            return self.add_transitions()

        if len(trans_RHS) == 2:
            transition = ((trans_RHS[0], trans_RHS[1]),)
        else:
            transition = []
            for i in range(len(trans_RHS)):
                if i % 2 == 0:
                    transition.append((trans_RHS[i], trans_RHS[i + 1]))
            transition = tuple(transition)

        if state not in self.transitions:
            self.transitions[state] = dict()
        if pop not in self.transitions[state]:
            self.transitions[state][pop] = dict()
        if letter not in self.transitions[state][pop]:
            self.transitions[state][pop][letter] = set()

        self.transitions[state][pop][letter].add(transition)
        return self.add_transitions()

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
