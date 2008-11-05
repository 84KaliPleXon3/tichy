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


import tichy
import tichy.gui as gui

# TODO: move this into prefs service ??
class ParamItem(tichy.Item):
    def __init__(self, service, key):
        self.service = service
        self.key = key
        
    # We override item.get_text cause we want to use our own view method
    # Instead ot relying on the item name
    def get_text(self):
        return self
    def view(self, parent):
        ret = gui.Box(parent, axis = 0, border = 0)
        gui.Label(ret, self.key)
        value = str(self.service[self.key])
        gui.Label(ret, value)
        return ret

class PhoneConf(tichy.Application):
    name = 'Phone'
     
    def run(self, parent):
        self.window = gui.Window(parent)
        frame = self.view(self.window, back_button=True)
        
        vbox = gui.Box(frame, axis=1, expand=True)
        
        prefs = tichy.Service('Prefs')
        phone = prefs['phone']
        
        # We create a list of actor on all the params we want to show
        self.params_list = tichy.List()
        for param in ['ring-tone', 'ring-volume']:
            param_item = ParamItem(phone, param)
            actor = tichy.Actor(param_item)
            self.params_list.append(actor)
        self.params_list.view(vbox)
        
        yield tichy.Wait(frame, 'back')     # Wait until the quit button is clicked
        self.window.destroy()                   # Don't forget to close the window
        
