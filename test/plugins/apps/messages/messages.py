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

import logging
logger = logging.getLogger('App.Messages')


class Message(tichy.Application):

    name = "Messages"
    icon = 'icon.png'
    category = 'main'

    def run(self, window):
        frame = self.view(window, back_button=True)

        vbox = gui.Box(frame, axis=1, expand=True)

        # We create a list of the sub applications actors
        list = tichy.ActorList()
        for app in [New, Inbox, Outbox]:
            actor = app.create_actor()
            list.append(actor)

        list.view(vbox)

        yield tichy.Wait(frame, 'back')


class Edit(tichy.Application):

    name = 'Edit'
    icon = 'icon.png'

    def run(self, window, sms):
        frame = self.view(window, title="Message", back_button=True)
        vbox = gui.Box(frame, axis=1, expand=True)
        self.sms = sms

        # The destination field
        hbox = gui.Box(vbox, axis=0)
        gui.Label(hbox, "to:")
        self.sms.number.create_actor().view(hbox, expand=True)

        # The message
        self.sms.text.view(vbox, editable=True, expand=True)

        frame.actor.new_action("Send").connect('activated', self.on_send)

        yield tichy.Wait(frame, 'back')

    def on_send(self, action, item, view):
        yield Sender(view.window, self.sms)


class Sender(tichy.Application):
    """Application that runs while we wait for the message to be sent.
    """

    def run(self, window, sms):
        frame = self.view(window, title="Sending...")
        vbox = gui.Box(frame, axis=1, expand=True)
        try:
            yield sms.send()
            yield tichy.Dialog(window, "Sent", "")
        except Exception, e:
            logger.error("Error: %s", e)
            yield tichy.Dialog(window, "Error", e)


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

    def run(self, window):
        frame = self.view(window, title="Inbox", back_button=True)
        vbox = gui.Box(frame, axis=1, expand=True)

        messages_service = tichy.Service('Messages')
        # We create a view on actors of every items in the outbox
        messages_service.inbox.actors_view(vbox)

        yield tichy.Wait(frame, 'back')


class Outbox(tichy.Application):

    name = "Outbox"
    icon = 'outbox_icon.png'
    design = 'Default'

    def run(self, window):
        frame = self.view(window, title="Outbox", back_button=True)
        vbox = gui.Box(frame, axis=1, expand=True)
        messages_service = tichy.Service('Messages')
        # We create a view on actors of every items in the outbox
        messages_service.outbox.actors_view(vbox)
        yield tichy.Wait(frame, 'back')


class Details(tichy.Application):

    name = "Details"

    def run(self, window, msg):
        frame = self.view(window, back_button=True)
        vbox = gui.Box(frame, axis=1, expand=True)
        msg.peer.view(vbox)
        msg.timestamp.view(vbox)
        yield tichy.Wait(frame, 'back')


class EditMessageService(tichy.Service):

    service = 'EditMessage'

    def edit(self, msg, window):
        return Edit(window, msg)

    def view_details(self, msg, window):
        return Details(window, msg)
