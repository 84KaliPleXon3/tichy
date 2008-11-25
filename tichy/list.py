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

from tichy.item import Item
from tichy.service import Service


class List(list, Item):
    """Base class for list

    It is better to use this class instead of python list in the case
    we want to monitor the list modifications. We can also create
    actor on a list.
    """

    def __init__(self, values=[]):
        list.__init__(self, values)
        Item.__init__(self)
        assert hasattr(self, '_Object__listeners'), self

    def clear(self):
        """Remove all the items from a list"""
        self[:] = []
        self.emit('cleared')
        self.emit('modified')

    def append(self, value):
        """Add a new item in the list"""
        list.append(self, value)
        self.emit('appened', value)
        self.emit('modified')

    def insert(self, index, value):
        list.insert(self, index, value)
        self.emit('inserted', index, value)
        self.emit('modified')

    def remove(self, value):
        """Remove one item from the list"""
        list.remove(self, value)
        self.emit('removed', value)
        self.emit('modified')

    def view(self, parent, **kargs):
        """Return a view of the list"""
        design = Service('Design')
        return design.view_list(parent, self, **kargs)

    def actors_view(self, parent, can_delete=False, **kargs):
        """Return a view that contains actors view to all the elements of this
        list

        arguments:

        - can_delete : if true we add a "Delete" action to every
          elements of the list
        """
        # This method is tricky. Modify with care !

        actors = ActorList()

        def on_delete(action, item, view):
            """called when the user wants to delete an item"""
            actors.remove(action.actor)
            self.remove(item)

        def on_modified(l):
            """Called when the original list is modified"""
            actors.clear()
            for e in self:
                actor = e.create_actor()
                if can_delete:
                    actor.new_action("Delete").connect('activated', on_delete)
                actors.append(actor)

        connection = self.connect('modified', on_modified)
        on_modified(self)
        view = actors.view(parent, **kargs)

        def on_destroyed(view, connection):
            self.disconnect(connection)

        # We don't forget to remove the connection
        view.connect('destroyed', on_destroyed, connection)

        return view


class ActorList(List):
    """Special List that only contains actors"""

    def view(self, parent, **kargs):
        design = Service('Design')
        return design.view_actor_list(parent, self, **kargs)
