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
from tichy.phone import TelNumber

import logging
logger = logging.getLogger('App.Logs')

class Logs(tichy.Application):
    name = "Logs"
    icon = 'icon.png'
    category = 'general' # So that we see the app in the launcher
     
    def run(self, window):
        w = gui.Window(window, modal=True)   # We run into a new modal window
        frame = self.view(w, back_button=True)
        
        vbox = gui.Box(frame, axis=1, expand=True)
        
        # We create a list of the sub applications actors
        list = tichy.ActorList()
        for app in [All]:
            actor = app.create_actor()
            list.append(actor)
        
        list.view(vbox)
        
        yield tichy.Wait(frame, 'back')     # Wait until the quit button is clicked
        w.destroy()                   # Don't forget to close the window
        
class All(tichy.Application):
    name = 'All'
    design = 'Default'
    
    def run(self, window):
        w = gui.Window(window, modal=True)   # We run into a new modal window
        frame = self.view(w, back_button=True)
        
        vbox = gui.Box(frame, axis=1, expand=True)
        
        gsm_service = tichy.Service('GSM')
        gsm_service.logs.actors_view(vbox)
        
        yield tichy.Wait(frame, 'back')     # Wait until the quit button is clicked
        w.destroy()                   # Don't forget to close the window
