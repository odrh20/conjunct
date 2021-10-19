[GitHub repository](https://github.com/odrh20/conjunct)

## Installing and Running Conjunct

This document gives the instructions to install and run the Conjunct program.




1. [Download Python3](https://www.python.org/downloads/).

    The program may not run on older versions of Python. As of September 3 2021, the latest version is 3.9.7, which works with Conjunct.




2. [Install Numpy](https://numpy.org/install/).

   You can download Numpy from the terminal with `pip`:

    ```
    pip install numpy
    ```

3. [Install Tabulate](https://pypi.org/project/tabulate/).

   You can download Tabulate from the terminal with `pip`:

    ```
    pip install tabulate
    ```

4. [Install func-timeout](https://pypi.org/project/func-timeout/).

   You can download func-timeout from the terminal with `pip`:

    ```
    pip install func-timeout
    ```

5. [Install Kivy](https://kivy.org/doc/stable/gettingstarted/installation.html).

   It should be possible to install with the following `pip` command:

    ```
    python -m pip install 'kivy[base]' kivy_examples
    ```
   If not, you may have to read the instructions and install via the link.


6. Now you should be able to launch Conjunct from the directory where all files are located by running the `main` file:

    ```
    python3 main.py
    ```
 
 
 
## Getting Started with Conjunct


Upon opening the tool, the user is presented with three buttons. The ‘Getting Started’ screen features a brief introduction to the tool and seeks to provide guidance to new users. It is advised to first learn about conjunctive grammars before SAPDA, since they are generally easier to understand. The principal functionality of the tool is accessed via the ‘Conjunctive Grammars‘ and ‘SAPDA’ buttons.

  
  
  
<img width="600" alt="Screenshot 2021-09-01 at 01 24 49" src="https://user-images.githubusercontent.com/73336800/137896515-f12bdbf6-623b-4530-8c14-91ca9978aa9d.png">




<img width="600" alt="Screenshot 2021-09-01 at 01 26 02" src="https://user-images.githubusercontent.com/73336800/137898239-4164aa21-2bd5-41ae-8e10-e15d7b331f42.png">




## Conjunctive Grammars

The ‘Conjunctive Grammars‘ screen contains three buttons. First, the user may view the tutorial to learn about conjunctive grammars. Then, they may instantiate a grammar by selecting an inbuilt example or by constructing their own.




<img width="600" alt="Screenshot 2021-09-01 at 02 40 21" src="https://user-images.githubusercontent.com/73336800/137898507-04d5d93b-42c5-4fb4-9127-141b8d29a0ff.png">




The tutorial intends to educate users familiar with context-free grammars about conjunctive grammars. It provides the formal definition of conjunctive grammars, and several example derivations.




<img width="600" alt="Screenshot 2021-09-01 at 01 27 12" src="https://user-images.githubusercontent.com/73336800/137899286-b7583716-a332-4853-ab74-59795777cc47.png">




Four different conjunctive grammars are built into the program.




<img width="600" alt="Screenshot 2021-09-01 at 12 50 47" src="https://user-images.githubusercontent.com/73336800/137899906-6a213b28-cc7d-4205-93c1-2367cf1fe497.png">




The user may alternatively construct a grammar from scratch. Instructions for making grammars are displayed on the screen.




<img width="600" alt="Screenshot 2021-09-01 at 01 40 27" src="https://user-images.githubusercontent.com/73336800/137900082-517e5d93-5459-41d9-90d0-e70d8eb73893.png">




Once a grammar has been built, the full description of the grammar is displayed. The user is presented with the choice of parsing a string with the CYK algorithm or converting the grammar to an equivalent SAPDA.




<img width="600" alt="Screenshot 2021-09-01 at 01 40 51" src="https://user-images.githubusercontent.com/73336800/137900184-22e84ed5-59e4-4994-851c-f78b89be9237.png">




To apply CYK to the grammar, it is converted into its equivalent Binary Normal Form. Then, the user may input any string into the text box to parse it.




<img width="600" alt="Screenshot 2021-09-01 at 01 49 57" src="https://user-images.githubusercontent.com/73336800/137900427-3c1adbab-233c-46f1-bde9-3f96bf6e1998.png">




If the input is accepted, a pop-up window will display the leftmost derivation. At each step, the position in the current derivation where a rule is next applied is highlighted in red. The window can be scrolled in vertical and horizontal directions when required for long derivations. If the input is rejected, this will also be shown on a pop-up window.




<img width="600" alt="Screenshot 2021-09-01 at 01 47 44" src="https://user-images.githubusercontent.com/73336800/137900598-a332d556-2ea3-4739-ac90-709bd10e9cb3.png">





## SAPDA

As with the grammars, there is a tutorial to learn about the SAPDA model, built-in examples and a custom SAPDA constructor.




<img width="600" alt="Screenshot 2021-09-01 at 02 40 41" src="https://user-images.githubusercontent.com/73336800/137902247-278cdc9f-1c4d-4b84-b57d-f90011c437db.png">




The tutorial introduces the formal definition of the SAPDA model and uses examples to demonstrate how transitions affect automaton configurations, especially with regards to conjunctive and synchronising transitions.




<img width="600" alt="Screenshot 2021-09-01 at 01 45 31" src="https://user-images.githubusercontent.com/73336800/137902843-bf48803e-af51-4c2f-980f-3817dd609f93.png">




Three different automata are built into the program.




<img width="600" alt="ChooseExampleSAPDA" src="https://user-images.githubusercontent.com/73336800/137902996-1297b05b-ceb5-4408-b0ae-8170307ffc1c.png">




The users may design their own SAPDA by inputting transitions into the text box. Instructions for building automata are displayed on the screen.

To minimise the required effort in building a SAPDA, the transitions are used to infer the remaining information. The input and stack alphabets are derived from the symbols read and pushed/popped to the stack, respectively. The initial state and stack symbol are taken from the topmost transition.




<img width="600" alt="Screenshot 2021-09-01 at 01 46 22" src="https://user-images.githubusercontent.com/73336800/137903140-039caaa6-0eb4-42aa-a938-064f748ca672.png">




Once a SAPDA object has been instantiated, the user can test it out on an input string.




<img width="600" alt="Screenshot 2021-09-02 at 01 16 53" src="https://user-images.githubusercontent.com/73336800/137904110-ec489939-b1c4-4d00-9e43-99987339e09c.png">




If an accepting configuration is reached, the entire computation will be displayed inside a pop-up box. For clarity, each configuration is rendered in tree format, rather than by using the formal denotation. In the event the string is rejected, or the computation times out, this information will be displayed.




<img width="600" alt="Screenshot 2021-09-02 at 01 15 09" src="https://user-images.githubusercontent.com/73336800/137904214-e6859046-0ae6-40a4-9f31-d24e26a66fd8.png">


