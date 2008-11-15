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
import tichy.gui as gui


class Category(tichy.Item):

    def __init__(self, category):
        self.category = category

    def get_text(self):
        return tichy.Text(self.category.split('/')[-1])

    def create_actor(self):
        actor = super(Category, self).create_actor()
        open_action = actor.new_action("Open")

        def on_open(action, self, view):
            yield Launcher(view.window, self.category)
        open_action.connect('activated', on_open)

        actor.default_action = open_action
        return actor


class Launcher(tichy.Application):
    """ The main application, used to start any other application
    """

    name = "Launcher"

    design = 'Grid'

    def run(self, window, category='main'):
        self.category = category
        main = self.category == 'main'
        self.window = tichy.gui.Window(window, modal=True)
        frame = self.view(self.window, title=self.category,
                          back_button=not main)
        # We populate the frame with all the applications
        self.list_view = None
        self._populate(frame)

        def run_lock(action, app, view):
            tichy.Service('ScreenLock').run(view.window)

        lock_item = frame.actor.new_action('Screen Lock')
        # the item does not really toggle back.
        # we will need a one that does 'launched' probably
        lock_item.connect('activated', run_lock)

        # If the design change we repopulate the frame This is a
        # little bit tricky. We use the 'changed' signal from the
        # Service('Design') base object...

        def on_design_changed(s, design):
            self._populate(frame)
        tichy.Service('Design').base.connect('changed', on_design_changed)

        quit_item = frame.actor.new_action('Quit')
        yield tichy.WaitFirst(tichy.Wait(quit_item, 'activated'),
                              tichy.Wait(frame, 'back'))
        self.window.destroy()

    def _is_sub_category(self, category):
        """Return true if the category is a sub category of the launcher
        category"""
        parts = category.split('/')
        return len(parts) == 2 and parts[0] == self.category

    def _populate(self, frame):
        if self.list_view:
            self.list_view.destroy()
        list = tichy.ActorList()
        categories = set()
        # View all the enabled applications in this category
        for app in tichy.Application.subclasses:
            if not app.name or not app.category:
                continue
            if app.category == self.category:
                actor = app.create_actor()
            elif self._is_sub_category(app.category) and \
                    not app.category in categories:
                actor = Category(app.category).create_actor()
                categories.add(app.category)
            else:
                continue
            list.append(actor)
        self.list_view = list.view(frame)
