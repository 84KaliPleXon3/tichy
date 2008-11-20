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

from tichy.item import Item
from tichy.service import Service


class Text(Item):
    """Base class for all text in tichy"""

    def __init__(self, value="", editable=False):
        super(Text, self).__init__()
        self.__value = unicode(value)
        self.editable = editable

    @classmethod
    def as_text(cls, value):
        if isinstance(value, cls):
            return value
        if value is None:
            return value
        return cls(unicode(value))

    def get_text(self):
        return self

    def __get_value(self):
        return self.__value

    def __set_value(self, v):
        self.__value = v
        self.emit('modified')

    value = property(__get_value, __set_value)

    def input_method(self):
        return None

    def __repr__(self):
        return self.__value.encode('ascii', 'replace')

    def __unicode__(self):
        return self.__value

    def __len__(self):
        return len(self.__value)

    def __getitem__(self, index):
        return self.__value[index]

    def __cmp__(self, o):
        return cmp(self.__value, unicode(o))

    def view(self, parent, editable=None, **kargs):
        from .gui import Label, Edit
        editable = editable if editable is not None else self.editable
        if not editable:
            ret = Label(parent, self.__value, **kargs)
        else:
            ret = Edit(parent, item=self, **kargs)

        connection = self.connect('modified', Text.on_modified, ret)
        ret.connect('destroyed', self.on_view_destroyed, connection)
        return ret

    def edit(self, window, **kargs):
        # first we get the appropriate TextEdit Service
        text_edit = Service('TextEdit')
        # Then we call the service with our text
        return text_edit.edit(
            window, self, input_method=self.input_method(), **kargs)

    def on_modified(self, view):
        view.text = self.__value

    def on_view_destroyed(self, view, connection):
        self.disconnect(connection)

    def create_actor(self):
        from actor import Actor
        ret = Actor(self)

        def on_edit(actor, item, view):
            yield item.edit(view.window)

        ret.new_action("Edit").connect('activated', on_edit)
        return ret
