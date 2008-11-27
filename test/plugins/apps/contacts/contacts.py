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

import logging
logger = logging.getLogger('app.contacts')

import tichy
import tichy.gui as gui


class Contacts(tichy.Application):

    name = 'Contacts'
    icon = 'icon.png'
    category = 'main'
    design = 'Default'

    def run(self, parent):
        self.window = gui.Window(parent)
        frame = self.view(self.window, back_button=True)

        vbox = gui.Box(frame, axis=1, expand=True)

        self.contacts_service = tichy.Service('Contacts')
        self.contacts = self.contacts_service.contacts
        self.contacts.actors_view(vbox)

        new_menu = frame.actor.new_action('New')
        new_menu.connect('activated', self.on_new)

        yield tichy.Wait(frame, 'back')
        self.window.destroy()

    def on_new(self, *args):
        contact = self.contacts_service.create()
        yield Contact(self.window, contact)
        self.contacts_service.add(contact)


class Contact(tichy.Application):

    design = 'Default'

    def run(self, window, contact):
        self.contact = contact
        self.name = "Edit %s" % contact.name
        self.window = gui.Window(window, modal=True)
        self.frame = self.view(self.window, back_button=True)

        vbox = gui.Box(self.frame, axis=1, expand=True)

        self.attr_list = tichy.ActorList()
        self.update()
        list_view = self.attr_list.view(vbox)

        yield tichy.Wait(self.frame, 'back')
        self.window.destroy()

    def on_add_attr(self, action, item, view, attr):
        value = attr.field.type()
        yield value.edit(self.window, name=attr.field.name)
        attr.value = value
        self.update()

    def update(self):
        """Update the list of attributes, and the possible actions"""
        logger.debug("update contact attributes")
        # This is a little bit messy, in the future we should have a
        # special Item for dictionary to hide this kind of things....
        self.attr_list.clear()
        for field in self.contact.fields:
            attr = self.contact.attributes[field.name]
            if attr.value:
                actor = attr.create_actor()
                if not attr.field.requiered:
                    actor.new_action('Delete').connect('activated',
                                                       self.on_delete_attr)
                self.attr_list.append(actor)

        self.frame.actor.clear()
        add_menu = self.frame.actor.new_action('Add')
        for field in self.contact.fields:
            attr = self.contact.attributes[field.name]
            if attr.value:
                continue
            add_attr = add_menu.new_action(attr.field.name)
            add_attr.connect('activated', self.on_add_attr, attr)

    def on_delete_attr(self, action, attr, view):
        self.attr_list.remove(action.actor)
        attr.value = None
        self.update()


class SelectContactApp(tichy.Application):

    name = "Select Contact"
    enabled = False

    def run(self, window):
        self.window = gui.Window(window)
        frame = self.view(self.window)

        vbox = gui.Box(frame, axis=1, expand=True)

        for contact in tichy.Service('Contacts').contacts:
            button = gui.Button(vbox)
            contact.get_text().view(button)
            button.connect('clicked', self.on_select, contact)

        # Wait until the quit button is clicked
        yield tichy.Wait(self.window, 'destroyed')
        yield self.ret

    def on_select(self, b, contact):
        self.ret = contact
        self.window.destroy()


class SelectContactService(tichy.Service):

    service = 'SelectContact'

    def select(self, window):
        return SelectContactApp(window)


class EditContactService(tichy.Service):

    service = 'EditContact'

    def edit(self, contact, window):
        yield Contact(window, contact)
