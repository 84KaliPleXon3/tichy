#    Tichy
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
import tichy.item as item 
from tichy.gui import Vect
import tichy.key

class TextEdit(tichy.Application):
    """A small application to test the keyboard widget"""
    name = 'TextEdit'
    def __init__(self, *args, **kargs):
        super(TextEdit, self).__init__(*args, **kargs)
    def run(self, parent, text = "", name = None, input_method = None):
        if isinstance(text, (str, unicode)): # TODO use a correct test
            text = tichy.Text(text)
        w = gui.Window(parent, modal = True)
        
        title = "Edit %s" % name if name else "Edit Text"
        frame = self.view(w, title=title, back_button=True)
        vbox = gui.Box(frame, axis=1, border=0, spacing=0)
        
        self.text = text
        self.text.view(vbox, editable=True, auto_keyboard=False, min_size=Vect(0, 0), expand=True)
        
        self.keyboard = tichy.Service('Keyboard').get()
        if input_method:
            self.keyboard.set_input_method(input_method)
            
        self.keyboard.view(vbox)
        
        yield tichy.Wait(frame, 'back')
        w.destroy()
        yield self.text.value
    
    def on_set_input(self, action, item, w, input):
        self.keyboard.set_input(input)
        
    def key_down(self, key):
        print 'TEST KEY DOWN', key
        
class MyTextEditService(tichy.Service):
    """Service to edit text
    
    By creating this service class, we allow any application in need
    of a text editor to use the applicaton we defined previously.
    """
    service = 'TextEdit'
    def edit(self, parent, text, name = None, input_method = None):
        """The only function defined in the TextEditService"""
        return TextEdit(parent, text, name=name, input_method=input_method)
        
        
        
