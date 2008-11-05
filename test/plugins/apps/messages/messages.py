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
logger = logging.getLogger('App.Messages')

class Message(tichy.Application):
    name = "Messages"
    icon = 'icon.png'
    category = 'general' # So that we see the app in the launcher
     
    def run(self, window):
        w = gui.Window(window, modal=True)   # We run into a new modal window
        frame = self.view(w, back_button=True)
        
        vbox = gui.Box(frame, axis=1, expand=True)
        
        # We create a list of the sub applications actors
        list = tichy.ActorList()
        for app in [New, Inbox, Outbox]:
            actor = app.create_actor()
            list.append(actor)
        
        list.view(vbox)
        
        yield tichy.Wait(frame, 'back')     # Wait until the quit button is clicked
        w.destroy()                   # Don't forget to close the window
        
class Edit(tichy.Application):
    name = 'Edit'
    icon = 'icon.png'
    
    def run(self, parent, sms):
        w = gui.Window(parent, modal=True)   # We run into a new modal window
        frame = self.view(w, title="Message", back_button=True)
        vbox = gui.Box(frame, axis=1, expand=True)
        self.sms = sms
        
        # The destination field
        hbox = gui.Box(vbox, axis=0)
        gui.Label(hbox, "to:")
        self.sms.number.create_actor().view(hbox, expand=True)
        
        # The message
        self.sms.text.view(vbox, editable=True, expand=True)
        
        frame.actor.new_action("Send").connect('activated', self.on_send)
        
        yield tichy.Wait(frame, 'back')     # Wait until the quit button is clicked
        w.destroy()
        
    def on_send(self, action, item, view):
        try:
            yield self.sms.send()
        except Exception, e:
            logger.error("Error: %s", e)
            yield tichy.Message(view.window, "Error", e)
        
class New(tichy.Application):
    name = 'New'
    enabled = False
    icon = 'icon.png'
    
    def run(self, parent):
        sms_service = tichy.Service('SMS')
        sms = sms_service.create()
        yield Edit(parent, sms)
        
class Inbox(tichy.Application):
    name = "Inbox"
    icon = 'inbox_icon.png'
    design = 'Default'
    
    def run(self, parent):
        w = gui.Window(parent, modal=True)   # We run into a new modal window
        frame = self.view(w, title="Inbox", back_button=True)
        vbox = gui.Box(frame, axis=1, expand=True)
        
        sms_service = tichy.Service('SMS')
        try:
            # This is just for testing...
            # The update method will try to get the messages from the sim
            yield sms_service.update()
        except Exception, e:
            logger.error("Error : %s", e)
            yield tichy.Message(w, "Error", e)
        
        # We create a view on actors of every items in the outbox
        sms_service.inbox.actors_view(vbox)
        
        yield tichy.Wait(frame, 'back')     # Wait until the quit button is clicked
        w.destroy()
        
class Outbox(tichy.Application):
    name = "Outbox"
    icon = 'outbox_icon.png'
    design = 'Default'
    
    def run(self, parent):
        w = gui.Window(parent, modal=True)   # We run into a new modal window
        frame = self.view(w, title="Outbox", back_button=True)
        vbox = gui.Box(frame, axis=1, expand=True)
        
        sms_service = tichy.Service('SMS')
        # We create a view on actors of every items in the outbox
        sms_service.outbox.actors_view(vbox)
        
        yield tichy.Wait(frame, 'back')     # Wait until the quit button is clicked
        w.destroy()

        
class EditMessageService(tichy.Service):
    service = 'EditSMS'
    def edit(self, sms, window):
        return Edit(window, sms)
