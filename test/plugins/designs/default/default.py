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

import tichy
from tichy.service import Service
from tichy import gui
from tichy.gui import Vect

# The default design

from application_view import ApplicationFrame


class ListView(gui.Scrollable):

    def __init__(self, parent, list, expand=True, **kargs):
        super(ListView, self).__init__(parent, item=list, axis=1, border=0,
                                       spacing=0, expand=expand)
        vbox = gui.Box(self, axis=1)
        # We add the already present items :
        for item in list:
            item.view(vbox)

        self.monitor(list, 'appened', self.on_appened, vbox)
        self.monitor(list, 'removed', self.on_removed, vbox)
        self.monitor(list, 'cleared', self.on_clear, vbox)

    def on_appened(self, list, value, view):
        value.view(view)

    def on_removed(self, list, value, view):
        for c in view.children[:]:
            c.destroy()
        for item in list:
            item.view(view)

    def on_clear(self, list, view):
        for c in view.children[:]:
            c.destroy()


class Default(Service):
    """Default Design service

    This design relies on tichy.gui module. It will draw list in a
    sliding list view.

    An actor will be seen as a button, pressing the button will make
    the list of actions appear on the bottom of the window.
    """

    enabled = True
    service = 'Design'
    name = 'Default'

    def __init__(self):
        self.selected = None

    def view_list(self, parent, list, **kargs):
        return ListView(parent, list, **kargs)

    def view_actor_list(self, parent, items, **kargs):
        return self.view_list(parent, items, **kargs)

    def view_actor(self, parent, actor, **kargs):
        ret = gui.Button(parent, item=actor, holdable=1000, **kargs)
        hbox = gui.Box(ret, axis=0, border=0)
        if actor.item.icon:
            icon_path = actor.item.path(actor.item.icon)
            icon = tichy.Image(icon_path, size=Vect(96, 96)).view(hbox)
        else:
            gui.Widget(hbox, min_size=Vect(0, 96))
        actor.item.get_text().view(hbox)

        def on_clicked(b, actor, self):
            self.select_actor(actor, b)
        ret.connect('clicked', on_clicked, actor, self)

        def on_holded(b, actor, self):
            self.select_actor(actor, b, use_default=False)
        ret.connect('holded', on_holded, actor, self)

        return ret

    def select_actor(self, actor, view, use_default=True):
        # If the actor has a default action and it is the only one,
        # then we start it
        if view == self.selected:
            action_bar = view.parent_as(ApplicationFrame).action_bar
            action_bar.clear()
            self.selected = None
            view.remove_tag('selected')
            return

        if self.selected:
            self.selected.remove_tag('selected')
        if actor.default_action and use_default:
            actor.default_action.activate(view)
            return
        self.selected = view
        view.add_tag('selected')
        # Otherwise we put the possible actions in the application
        # action_bar
        action_bar = view.parent_as(ApplicationFrame).action_bar
        action_bar.set_actor(actor, view)

        # We have to make sure we remove the reference to this view if
        # it get destroyed this is a little tricky...

        def on_destroy(b):
            self.selected = None
        self.selected.connect('destroyed', on_destroy)

    def view_application(self, parent, app, **kargs):
        return ApplicationFrame(parent, app, **kargs)
