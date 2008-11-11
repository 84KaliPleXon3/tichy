#    Tichy
#    copyright 2008 Guillaume Chereau (charlie@openmoko.org)
#
#    This file is part of Tichy.
#
#    Tichy is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Tichy is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Tichy.  If not, see <http://www.gnu.org/licenses/>.


from button import Button
from label import Label
from tichy.service import Service
from tichy.tasklet import Tasklet
from tichy.text import Text
import tichy.key


class Edit(Label, Button):

    def __init__(self, parent, item=None, auto_keyboard=True, **kargs):
        assert item is not None
        text = item.value
        super(Edit, self).__init__(parent, text=text, item=item, **kargs)
        self.auto_keyboard = auto_keyboard

    def click(self):
        if self.auto_keyboard:
            # first we get the appropriate TextEdit Service
            text_edit = Service('TextEdit')
            # Then we call the service with our text

            def on_done(text):
                self.text = text
                self.item.value = text
            text_edit.edit(self.window, self.text).start(on_done)

    def key_down(self, key):
        if key.key == tichy.key.K_BACKSPACE:
            self.item.value = self.item.value[:-1]
        elif key.key == tichy.key.K_RETURN:
            self.item.value += '\n'
        elif key.unicode:
            self.item.value += key.unicode

        self.text = self.item.value
        return True
