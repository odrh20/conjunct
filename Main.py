from Computation import *
from SAPDA import *
from CG import *
from Derivation import *
from prompt_toolkit import print_formatted_text, HTML


def run():
    try:
        choice = int(input(
            "\n\nEnter Choice:"
            "\n1. View tutorial."
            "\n2. Make a SAPDA."
            "\n3. Make a Conjunctive Grammar."
            "\n4. Quit."
            "\nEnter choice : "))
        if choice == 1:
            print("\nWork in progress.\n")
            run()
        elif choice == 2:
            make_sapda()
        elif choice == 3:
            make_CG()
        elif choice == 4:
            print("\nExiting program.\n")

        else:
            raise ValueError

    except ValueError:
        print("\nInvalid input. Try again.\n")
        run()

    return False


def make_sapda():
    try:
        choice = int(input("\nEnter Choice: "
                           "\n1. Choose an example SAPDA."
                           "\n2. Design your own SAPDA."
                           "\n3. Return to start."
                           "\nEnter choice : "))
        if choice == 1:
            choose_sapda()
        elif choice == 2:
            sapda = SAPDA(user=True)
            print(sapda)
            choose_sapda_action(sapda)
        elif choice == 3:
            main()
        else:
            raise ValueError
    except ValueError:
        print("\nInvalid input. Try again.\n")
        return make_sapda()


def choose_sapda():
    try:
        choice = int(input(f"\nEnter Choice: \n1. {sapda1.name} \n2. {sapda2.name} \n"
                           f"3. {sapda3.name} \n4. Return to start.\nEnter choice : "))

        sapda = None
        if choice == 1:
            sapda = sapda1

        elif choice == 2:
            sapda = sapda2

        elif choice == 3:
            sapda = sapda3

        elif choice == 4:
            main()
        else:
            raise ValueError

        print(sapda)
        choose_sapda_action(sapda)

    except ValueError:
        print("\nInvalid input. Try again.\n")
        return choose_sapda()


def choose_sapda_action(sapda):
    #print(sapda)
    try:
        choice = int(input(
            "\nEnter Choice:"
            "\n1. Run the SAPDA on an input string."
            "\n2. Return to start."
            "\nEnter choice : "))

        if choice == 1:
            input_string = str(input("Enter an input string:  "))
            initial_config = Computation(sapda, input_string)
            print("\n", initial_config.run_machine())
            choose_sapda_action(sapda)

        elif choice == 2:
            main()

        else:
            raise ValueError

    except ValueError:
        print("\nInvalid input. Try again.\n")
        return choose_sapda_action(sapda)


def make_CG():
    try:
        choice = int(input("\nEnter Choice: "
                           "\n1. Choose an example Conjunctive Grammar."
                           "\n2. Design your own Conjunctive Grammar."
                           "\n3. Return to start."
                           "\nEnter choice : "))
        if choice == 1:
            choose_CG()
        elif choice == 2:
            cg = CG(user=True)
            print(cg)
            choose_CG_action(cg)
        elif choice == 3:
            main()
        else:
            raise ValueError
    except ValueError:
        print("\nInvalid input. Try again.\n")
        return make_CG()


def choose_CG():
    try:
        choice = int(input(f"\nEnter Choice: \n1. {cg1.name} \n2. {cg2.name} \n"
                           f"3. {cg3.name} \n4. Return to start.\nEnter choice : "))

        cg = None
        if choice == 1:
            cg = cg1

        elif choice == 2:
            cg = cg2

        elif choice == 3:
            cg = cg3

        elif choice == 4:
            main()
        else:
            raise ValueError

        print(cg)
        choose_CG_action(cg)

    except ValueError:
        print("\nInvalid input. Try again.\n")
        return choose_CG()


def choose_CG_action(cg):
    try:
        choice = int(input(
            "\nEnter Choice:"
            "\n1. Derivation."
            "\n2. Convert grammar to an equivalent SAPDA."
            "\n3. Return to start."
            "\nEnter choice : "))

        if choice == 1:
            input_string = str(input("Enter a derivation string:  "))
            derivation = Derivation(cg, Word(cg, input_string))
            print(derivation.get_derivation())
            choose_CG_action(cg)

        elif choice == 2:
            sapda = cg.convert_to_sapda()
            print(sapda)
            return choose_sapda_action(sapda)

        elif choice == 3:
            main()
        else:
            raise ValueError

    except ValueError:
        print("\nInvalid input. Try again.\n")
        return choose_CG_action(cg)


def main():
    print_formatted_text(HTML('<ansigreen><u>\nWelcome to the Synchronised Alternating Pushdown Automata Tool'
                              '\n</u></ansigreen>'))
    #print("\nWelcome to the Synchronised Alternating Pushdown Automata Tool\n")
    running = True
    while running:
        running = run()


if __name__ == '__main__':
    main()