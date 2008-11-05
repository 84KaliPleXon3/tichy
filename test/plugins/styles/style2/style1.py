
import tichy.gui as gui
import tichy.item.style as style
from tichy import item



class Style1(style.Style):
    def name(self):
        return "style1"
        
    @classmethod
    def code(cls):
        return {
            'background' : None,
            # XXX: How to decide of the priority between gui.Edit and gui.Button ?? Need to add a kind of sorting in the style parts
            gui.Edit : {'background' : style.Frame(gui.Image(Style1.path('edit_frame.png')))},
            gui.Button : {'background' : style.Frame(gui.Image(Style1.path('button_frame.png')))},
            gui.ApplicationFrame.Bar : {'background' : style.Frame(gui.Image(Style1.path('bar_frame.png')))},
            gui.ApplicationFrame.Content : {'background' : style.Frame(gui.Image(Style1.path('content_frame.png')))},
            
            'pressed-style' : {'background' : style.Frame(gui.Image(Style1.path('button_pressed_frame.png')))},
            
            item.Menu : {
                'children-style' : {
                    gui.Button : {'background' : style.Frame(gui.Image(Style1.path('menu_button_frame.png')))},
                }
            },
            
            item.List : {
                'children-style' : {
                    gui.Button : {'background' : style.Frame(gui.Image(Style1.path('list_button_frame.png')))},
                }
            }
        }
