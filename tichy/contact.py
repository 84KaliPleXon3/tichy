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


# TODO: Redo the whole contact things. We should have a single contact
# class, no subclass for different backends, instead we have
# ContactStorage classes where we define storage functions.  A contact
# should have any fields (dictionary style), and each storage can
# define which fields are supported.


class Contact(tichy.Item):
    """base class for tichy's contacts"""

    storage = None

    class Field(tichy.Item):
        """Representation of a field in a given contact
        """

        def __init__(self, contact, name, type, requiered=False):
            """Create a new field representation

            Parameters:

            - contact : the contact the field belong to

            - name : the name of the attribute in the contact

            - type : the type of the field

            - requiered : If set to True, then the field is requiered
              (we can't set it to None)
            """
            super(Contact.Field, self).__init__()
            self.contact = contact
            self.name = name
            self.type = type
            self.requiered = requiered

        def __get_value(self):
            return getattr(self.contact, self.name)

        def __set_value(self, value):
            assert value is None or isinstance(value, self.type)
            return setattr(self.contact, self.name, value)

        value = property(__get_value, __set_value)

        def get_text(self):
            return self

        def __unicode__(self):
            return unicode(self.name)

        def view(self, parent):
            ret = gui.Box(parent, axis=0, border=0)
            gui.Label(ret, self.name)
            self.value.view(ret)
            return ret

        def create_actor(self):
            actor = super(Contact.Field, self).create_actor()
            actor.new_action('Edit').connect('activated', self.on_edit)
            return actor

        def on_edit(self, action, attr, view):
            yield self.value.edit(view.window, name=self.name)

        @classmethod
        def import_(cls, contact):
            """create a new contact from an other contact)
            """
            yield None

    def __init__(self, name, tel=None, note=None, **kargs):
        """Create a new contact
        """
        super(Contact, self).__init__()
        self.name = tichy.Text.as_text(name)
        self.tel = tichy.TelNumber.as_text(tel)
        self.note = tichy.Text.as_text(note)

    def get_fields(self):
        """return all the fields of the contact"""
        return [Contact.Field(self, 'name', tichy.Text, True),
                Contact.Field(self, 'tel', tichy.TelNumber),
                Contact.Field(self, 'note', tichy.Text)]

    def get_text(self):
        return self.name

    def view(self, parent, **kargs):
        return self.name.view(parent, **kargs)

    def create_actor(self):
        actor = tichy.Item.create_actor(self)
        actor.new_action("Call").connect('activated', self.on_call)
        actor.new_action("Edit").connect('activated', self.on_edit)

        for cls in Contact.subclasses:
            if isinstance(self, cls):
                continue
            import_ = actor.new_action("Copy to %s" % cls.storage)
            import_.connect('activated', self.on_copy_to, cls)

        return actor

    def on_copy_to(self, action, contact, view, cls):
        contact = yield cls.import_(self)
        tichy.Service('Contacts').add(contact)

    def on_call(self, action, contact, view):
        if not self.tel:
            yield gui.Message(view.window, "Contact has no tel")
        else:
            caller = tichy.Service('Caller')
            yield caller.call(view.window, self.tel)

    def on_edit(self, item, contact, view):
        editor = tichy.Service('EditContact')
        return editor.edit(self, view.window)


class PhoneContact(Contact):
    storage = 'Phone'

    @classmethod
    def import_(cls, contact):
        assert not isinstance(contact, PhoneContact)
        yield PhoneContact(contact.name, tel=contact.tel)


class ContactsService(Service):

    service = 'Contacts'

    def __init__(self):
        self.contacts = tichy.List()
        fabien = PhoneContact('Fabien', tel='0478657392', note='Hello')
        self.add(fabien)
        etienne = PhoneContact('Etienne', tel='044569892')
        self.add(etienne)

    def add(self, contact):
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
            if c.tel == number:
                return c

    def create(self):
        name = self.new_name()
        return PhoneContact(name)
