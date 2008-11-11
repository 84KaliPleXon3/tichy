#    Tichy
#
#    copyright 2008 Guillaume Chereau (charlie@openmoko.org)
#
#    This file is part of Tichy.
#
#    Tichy is free software: you can redistribute it and/or modify it
#    under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Tichy is distributed in the hope that it will be useful, but
#    WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Tichy.  If not, see <http://www.gnu.org/licenses/>.

import tichy
import tichy.gui as gui
from tichy.menu import Menu
from tichy.list import List
from tichy.style import Style, Font, Frame, Tag


class Style2(Style):
    """A simple style for tichy"""

    name = "black style"

    @classmethod
    def code(cls):
        return {
            gui.Screen: {'background': tichy.Image(
                    Style2.path('background.png'))},
            # 'background' : None,
            'font': Font(None, 26),
            gui.Edit: {'background': Frame(tichy.Image(
                        Style2.path('edit_frame.png')))},
            gui.Button: {
                'background': Frame(tichy.Image(
                        Style2.path('button_frame.png'))),
                'min-size': gui.Vect(3, 3) * 32,
            },
            # The tag here is a filter on the widgets that have this
            # string in there keys
            Tag('application-bar'): {
                'background': Frame(tichy.Image(
                        Style2.path('bar_frame.png'))),
                'children-style': {
                    'background': None,
                    Tag('selected'): {'background': Frame(tichy.Image(
                                Style2.path('button_pressed_frame.png')))},
                    Tag('back-button'): {'background': Frame(tichy.Image(
                                Style2.path('button_frame.png')))},
                }
            },

            'pressed-style': {'background': Frame(tichy.Image(
                        Style2.path('button_pressed_frame.png')))},
            Tag('selected'): {'background': Frame(tichy.Image(
                        Style2.path('button_pressed_frame.png')))},

            Menu: {
                'children-style': {
                    gui.Button: {'background': Frame(tichy.Image(
                                Style2.path('menu_button_frame.png')))},
                }
            },

            gui.Table: {'spacing': 16},

            List: {
                'border': 16,
                'children-style': {
                    gui.Button: {
                        'background': Frame(tichy.Image(
                                Style2.path('list_button_frame.png'))),
                        Tag('selected'): {
                            'background': Frame(
                                tichy.Image(
                                    Style2.path(
                                        'button_pressed_frame.png')))},
                    },
                    Tag('grid-item'): {
                        'min-size': gui.Vect(128, 128)
                    },
                },
            },
        }
