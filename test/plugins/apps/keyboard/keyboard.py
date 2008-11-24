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
from tichy import gui
from tichy.gui import Vect
import tichy.key

from layout import lowercase_layout, uppercase_layout, number_layout, \
    punctuation_layout, Key

# TODO: Make the keyboard faster !!!


class Keyboard(tichy.Item):

    def __init__(self, layouts=[lowercase_layout, uppercase_layout,
                                number_layout, punctuation_layout]):
        super(Keyboard, self).__init__()
        self.layouts = layouts
        self.layout = layouts[0]

    def view(self, parent, item=None, **kargs):
        ret = gui.Box(parent, axis=1, border=0, spacing=0)
        preview = tichy.Text('')
        preview.view(ret, optimal_size=Vect(128, 64), min_size=Vect(128, 64))
        KeyboardWidget(ret, item=self, preview=preview, **kargs)
        return ret

    def next_layout(self):
        for i, l in enumerate(self.layouts):
            if l is self.layout:
                break
        i = (i+1) % len(self.layouts)
        self.set_layout(self.layouts[i])

    def set_layout(self, layout):
        self.layout = layout
        self.emit('layout-changed')

    def set_input_method(self, method):
        if method == 'number':
            self.set_layout(number_layout)


class KeyboardWidget(gui.Fixed):

    def __init__(self, parent, preview=None, item=None,
                 min_size=Vect(64 * 7, 64 * 5), **kargs):
        super(KeyboardWidget, self).__init__(parent, item=item,
                                             min_size=min_size, **kargs)
        self.keys = []
        self.preview = preview
        self.update_layout(self.item.layout)
        self.item.connect('layout-changed', self.on_keyboard_update_layout)

    def on_keyboard_update_layout(self, keyboard):
        self.update_layout(keyboard.layout)

    def update_layout(self, layout):
        for k in self.keys:
            k.destroy()
        self.keys = []

        view = None
        # We create all the keys
        for i, key in enumerate(layout.keys):
            view = key.view(self, same_as=view)
            self.keys.append(view)

        # We connect all the keys
        for key in self.keys:
            key.connect('clicked', self.on_click)

    def on_click(self, key):
        key = key.item
        if key.key == tichy.key.K_NEXT_LAYOUT:
            self.item.next_layout()
            return
        tichy.mainloop.post_key_event('down', key.key, key.mod, key.unicode)
        self.preview.value = ''

    def mouse_motion(self, pos):
        # We don't do it the normal way for the keyboard because we
        # want the user to be able to stay clicked and move the mouse
        # to press any of the keys.
        super(KeyboardWidget, self).mouse_motion(pos)
        if self.focused and not pos - self.focused.pos in self.focused.rect:
            self.focused.mouse_down_cancel()
            for k in self.keys:
                if pos - k.pos in k.rect:
                    k.mouse_down(pos - k.pos)
                    self.focus_child(k)
                    self.preview.value = k.item.unicode
                    return

    def do_organize(self):
        for c in self.children:
            c.do_organize()

    def mouse_down(self, pos):
        for k in self.keys:
            if pos - k.pos in k.rect:
                self.preview.value = k.item.unicode
        return super(KeyboardWidget, self).mouse_down(pos)


class KeyboardService(tichy.Service):

    service = 'Keyboard'

    def get(self):
        return Keyboard()
