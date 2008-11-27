# coding=utf8
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
logger = logging.getLogger('Contact')

from tichy.service import Service, ServiceUnusable
from tichy.object import Object

import tichy
import tichy.gui as gui


# TODO: Redo the whole contact things. We should have a single contact
# class, no subclass for different backends, instead we have
# ContactStorage classes where we define storage functions.  A contact
# should have any fields (dictionary style), and each storage can
# define which fields are supported.

# TODO: also the Field / Attr thing is good, but it should be a subset
# of a higher level module Struct.


class ContactField(object):
    """Represent a field in a contact class

    When we create a new Contact type, we can decide what fields can
    be used with it. For example a SIM contact will only have a name
    and tel fields.

    typical fields are : name, tel, note...

    A Field is a python descriptor. It means we can declare fields in
    a Contact class, and when we try to access them we will get the
    attribute instead of the field itself.
    """

    def __init__(self, name, type, requiered=False):
        """Create a new field

        Parameters:

        - name : the name of the field

        - type : the type, it should be a tichy.Item class

        - requiered : If set to True then the field is compulsory
        """
        self.name = name
        self.type = type
        self.requiered = requiered

    def __get__(self, obj, type=None):
        return obj.attributes[self.name].value

    def __set__(self, obj, value):
        obj.attributes[self.name].value = value

    def __repr__(self):
        return self.name


class ContactAttr(tichy.Item):
    """represent an attribute of a contact

    This is different from the field. The filed contains only meta
    information about a contact attribute, the attribute contains the
    value itself.
    """

    def __init__(self, contact, field):
        self.contact = contact
        self.field = field

    def get_text(self):
        return self

    def __repr__(self):
        return "%s : %s" % (self.field.name, self.value)

    def __unicode__(self):
        return unicode(self.field.name)

    def view(self, parent):
        ret = gui.Box(parent, axis=0, border=0)
        gui.Label(ret, "%s:" % self.field.name)
        if self.value:
            self.value.view(ret)
        return ret

    def create_actor(self):
        actor = super(ContactAttr, self).create_actor()
        actor.new_action('Edit').connect('activated', self.on_edit)
        return actor

    def __get_value(self):
        return getattr(self.contact, '_attr_%s_' % self.field.name, None)

    def __set_value(self, value):
        value = self.field.type.as_type(value)
        setattr(self.contact, '_attr_%s_' % self.field.name, value)
        if value is not None:
            value.connect('modified', self._on_value_modified)
        self.emit('modified')

    value = property(__get_value, __set_value)

    def _on_value_modified(self, value):
        self.emit('modified')

    def on_edit(self, action, attr, view):
        assert self.value
        yield self.value.edit(view.window, name=self.field.name)


class Contact(tichy.Item):
    """base class for tichy's contacts

    We have to redo this class better. So far a contact can only have
    one backend. The backend method (import_) being a class method. If
    we want to have several backends per contacts we need (and should)
    to change that...
    """

    storage = None

    Field = ContactField        # Alias for the ContactField class

    def __init__(self, **kargs):
        """Create a new contact
        """
        super(Contact, self).__init__()
        self.attributes = dict((x.name, ContactAttr(self, x)) \
                                   for x in self.fields)
        for k, a in self.attributes.items():
            if k in kargs:
                a.value = kargs[k]
            a.connect('modified', self._on_attr_modified)

    def _on_attr_modified(self, attr):
        self.emit('modified')

    def get_text(self):
        return self.name

    def view(self, parent, **kargs):
        return self.name.view(parent, **kargs)

    def create_actor(self):
        actor = tichy.Item.create_actor(self)
        actor.new_action("Call").connect('activated', self.on_call)
        actor.new_action("Edit").connect('activated', self.on_edit)
        actor.new_action("Delete").connect('activated', self.on_delete)

        for cls in Contact.subclasses:
            if isinstance(self, cls):
                continue
            import_ = actor.new_action("Copy to %s" % cls.storage)
            import_.connect('activated', self.on_copy_to, cls)

        return actor

    def on_copy_to(self, action, contact, view, cls):
        try:
            contact = yield cls.import_(self)
            tichy.Service('Contacts').add(contact)
        except Exception, e:
            logger.error("can't import contact : %s", e)
            yield tichy.Dialog(view.window, "Error",
                               "can't import the contact")

    def on_call(self, action, contact, view):
        if not self.tel:
            yield gui.Message(view.window, "Contact has no tel")
        else:
            caller = tichy.Service('Caller')
            yield caller.call(view.window, self.tel)

    def on_edit(self, item, contact, view):
        editor = tichy.Service('EditContact')
        return editor.edit(self, view.window)

    def on_delete(self, item, contact, view):
        try:
            yield contact.delete()
            tichy.Service('Contacts').remove(contact)
        except Exception, e:
            logger.error("can't delete contact : %s", e)
            yield tichy.Dialog(view.window, "Error",
                               "can't delete the contact")

    def delete(self):
        """delete the contact

        This perform the action to delete a contact
        """
        yield None

    def to_dict(self):
        """return all the attributes in a python dict"""
        return dict((str(f.field.name), unicode(f.value)) \
                        for f in self.attributes.values() \
                        if f.value is not None)

    @classmethod
    def import_(cls, contact):
        """create a new contact from an other contact)
        """
        yield None


class PhoneContact(Contact):
    """Contact that is stored on the phone"""

    storage = 'Phone'

    name = ContactField('name', tichy.Text, True)
    tel = ContactField('tel', tichy.TelNumber)
    note = ContactField('note', tichy.Text)
    fields = [name, tel, note]

    def __init__(self, **kargs):
        super(PhoneContact, self).__init__(**kargs)
        self.connect('modified', self._on_modified)

    def _on_modified(self, contact):
        logger.info("Phone contact modified")
        yield self.save()

    @classmethod
    def import_(cls, contact):
        """import a contact into the phone"""
        assert not isinstance(contact, PhoneContact)
        yield PhoneContact(name=contact.name, tel=contact.tel)

    @classmethod
    def save(cls):
        """Save all the phone contacts"""
        logger.info("Saving phone contacts")
        contacts = tichy.Service('Contacts').contacts
        data = [c.to_dict() for c in contacts if isinstance(c, PhoneContact)]
        tichy.Persistance('contacts/phone').save(data)
        yield None

    @classmethod
    def load(cls):
        """Load all the phone contacts

        Return a list of all the contacts
        """
        logger.info("Loading phone contacts")
        ret = []
        data = tichy.Persistance('contacts/phone').load()
        for kargs in data:
            contact = PhoneContact(**kargs)
            ret.append(contact)
        yield ret


class ContactsService(Service):

    service = 'Contacts'

    def __init__(self):
        self.contacts = tichy.List()

    @tichy.tasklet.tasklet
    def load_all(self):
        """load all the contacts from all the sources

        We need to call this before we can access the contacts
        """
        for cls in Contact.subclasses:
            logger.info("loading contacts from %s" % cls.storage)
            try:
                contacts = yield cls.load()
            except Exception, e:
                logger.warning("can't get contacts : %s", e)
                continue
            for c in contacts:
                assert isinstance(c, Contact), type(c)
                self.contacts.append(c)
        logger.info("got %d contacts", len(self.contacts))

    def add(self, contact):
        self.contacts.append(contact)

    def remove(self, contact):
        self.contacts.remove(contact)

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
        return PhoneContact(name=name)
