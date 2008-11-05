
import tichy
import tichy.gui as gui
from tichy.menu import Menu
from tichy.list import List
from tichy.style import Style, Font, Frame, Tag

class Style2(Style):
    name = "black style"
        
    @classmethod
    def code(cls):
        return {
            gui.Screen : {'background' : tichy.Image(Style2.path('background.png'))},
            # 'background' : None,
            'font' : Font(None, 26),
            gui.Edit : {'background' : Frame(tichy.Image(Style2.path('edit_frame.png')))},
            gui.Button : {
                'background' : Frame(tichy.Image(Style2.path('button_frame.png'))),
                'min-size' : gui.Vect(3,3) * 32,
            },
            # The tag here is a filter on the widgets that have this string in there keys
            Tag('application-bar') : {
                'background' : Frame(tichy.Image(Style2.path('bar_frame.png'))),
                'children-style' : {
                    'background': None,
                    Tag('selected') : {'background' : Frame(tichy.Image(Style2.path('button_pressed_frame.png')))},
                    Tag('back-button') : {'background' : Frame(tichy.Image(Style2.path('button_frame.png')))},
                }
            },
            # Tag('application-content') : {'background' : Frame(tichy.Image(Style2.path('content_frame.png')))},
            
            'pressed-style' : {'background' : Frame(tichy.Image(Style2.path('button_pressed_frame.png')))},
            Tag('selected') : {'background' : Frame(tichy.Image(Style2.path('button_pressed_frame.png')))},
            
            Menu : {
                'children-style' : {
                    gui.Button : {'background' : Frame(tichy.Image(Style2.path('menu_button_frame.png')))},
                }
            },
            
            gui.Table : {
                'spacing' : 16,
            },
        
            List : {
                'border' : 16,
                'children-style' : {
                    gui.Button : {
                        'background' : Frame(tichy.Image(Style2.path('list_button_frame.png'))),
                        Tag('selected') : {'background' : Frame(tichy.Image(Style2.path('button_pressed_frame.png')))},
                    },
                    Tag('grid-item'): {
                        'min-size' : gui.Vect(128,128)
                    },
                },
            },
            
            # gui.ScrollableSlide : {'background' : Frame(tichy.Image(Style2.path('button_frame.png')))},
        }
