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

from tichy.service import Service, ServiceUnusable
from tichy.object import Object

import tichy
import tichy.gui as gui

from tichy.phone import TelNumber


class Contact(dict, tichy.Item):

    def __init__(self, name, source=None):
        """Create a new contact

        source can be :

        - 'sim'
        """
        super(Contact, self).__init__()
        self['name'] = name
        if source == 'sim':
            self.icon = 'pics/sim.png'

    def get_text(self):
        return self['name']

    def view(self, parent, editable=True):
        return gui.Label(parent, unicode(self.name))

    def create_actor(self):
        actor = tichy.Item.create_actor(self)
        actor.new_action("Call").connect('activated', self.on_call)
        actor.new_action("Edit").connect('activated', self.on_edit)
        return actor

    def on_call(self, action, contact, view):
        if not 'tel' in self:
            yield gui.Message(view.window, "Contact has no tel")
        else:
            caller = tichy.Service('Caller')
            yield caller.call(view.window, str(self['tel']))

    def on_edit(self, item, contact, view):
        editor = tichy.Service('EditContact')
        return editor.edit(self, view.window)


class ContactsService(Service):

    service = 'Contacts'

    def __init__(self):
        self.contacts = tichy.List()
        fabien = self.create('Fabien')
        fabien['tel'] = TelNumber('0478657392')
        fabien['note'] = tichy.Text('hello')

        etienne = self.create('Etienne')
        etienne['tel'] = TelNumber('044569892')

    def create(self, name=None, source=None):
        name = name or self.new_name()
        contact = Contact(tichy.Text(name), source=source)
        self.contacts.append(contact)
        return contact

    def new_name(self):
        name = 'new'
        i = 2
        while name in [unicode(c.name) for c in self.contacts]:
            name = "new%d" % i
            i += 1
        return name

    def find_by_number(self, number):
        for c in self.contacts:
            if 'tel' in c and c['tel'] == number:
                return c
