
import tichy
import tichy.gui as gui
from tichy.menu import Menu
from tichy.style import Style, Font, Frame, Tag

class MyStyle(Style):
    name = "cool style"
        
    @classmethod
    def code(cls):
        return {
            'background' : None,
            'font' : Font(None, 16),
            gui.Edit : {'background' : Frame(tichy.Image(MyStyle.path('edit_frame.png')))},
            gui.Button : {
                'background' : Frame(tichy.Image(MyStyle.path('button_frame.png'))),
                'min-size' : gui.Vect(3,3) * 32,
            },
            # The tag here is a filter on the widgets that have this string in there keys
            Tag('application-bar') : {
                'background' : Frame(tichy.Image(MyStyle.path('bar_frame.png'))),
                'children-style' : {
                    'background': None,
                    Tag('selected') : {'background' : Frame(tichy.Image(MyStyle.path('button_pressed_frame.png')))},
                    Tag('back-button') : {
                        'background' : Frame(tichy.Image(MyStyle.path('button_frame.png'))),
                    },
                }
            },
            Tag('application-content') : {'background' : Frame(tichy.Image(MyStyle.path('content_frame.png')))},
            
            'pressed-style' : {'background' : Frame(tichy.Image(MyStyle.path('button_pressed_frame.png')))},
            Tag('selected') : {'background' : Frame(tichy.Image(MyStyle.path('button_pressed_frame.png')))},
            
            Menu : {
                'children-style' : {
                    gui.Button : {'background' : Frame(tichy.Image(MyStyle.path('menu_button_frame.png')))},
                }
            },
            
            gui.Box : {'spacing' : 8, 'border': 4},
            
            tichy.List : {
                'border' : 16,
                'children-style' : {
                    gui.Box : {'spacing' : 8, 'border': 8},
                    gui.Table : {'spacing' : 32},
                    gui.Button : {
                        'background' : Frame(tichy.Image(MyStyle.path('button_frame.png'))),
                        Tag('selected') : {'background' : Frame(tichy.Image(MyStyle.path('button_pressed_frame.png')))},
                    },
                    Tag('grid-item'): {
                        'background' : None,
                        'min-size' : gui.Vect(96,128),
                        'children-style': {
                            gui.Frame : {
                                'background' : Frame(tichy.Image(MyStyle.path('button_frame.png'))),
                                'min-size' : gui.Vect(96,96),
                            },
                            gui.Label : {'background' : None},
                            gui.Box : {'background' : None},
                        }
                    },
                },
            },
            
            gui.ScrollableSlide : {'background' : Frame(tichy.Image(MyStyle.path('button_frame.png')))},
        }
