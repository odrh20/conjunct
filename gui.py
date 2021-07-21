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


from CG import *
from SAPDA import *
from Parser import *


# Define our different screens

class StartWindow(Screen):
    pass


class CGWindow(Screen):
    pass


class SAPDAWindow(Screen):
    pass


class ChooseCGWindow(Screen):
    pass


class ChooseSAPDAWindow(Screen):
    pass


class ChooseCGActionWindow(Screen):
    pass


class ChooseSAPDAActionWindow(Screen):
    pass


class CYKParseWindow(Screen):
    pass


class GenerateParseWindow(Screen):
    pass



class WindowManager(ScreenManager):
    pass


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



    def build(self):

        #Window.clearcolor = (1, 1, 1, 1)
        kv = Builder.load_file('gui.kv')

        return kv


if __name__ == '__main__':
    ConjunctApp().run()

