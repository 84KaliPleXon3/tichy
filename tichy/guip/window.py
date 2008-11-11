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


from widget import Widget
from tichy.tasklet import Tasklet

import logging
logger = logging.getLogger('gui.Window')


class Window(Widget):
    """Special widget that can receive events from an external source

    A window can also be an event source for other sub window. We can
    also block the events to all but one child, making it a modal
    dialog.
    """

    def __init__(self, parent, modal=True, events_source=None, **kargs):
        super(Window, self).__init__(parent, **kargs)
        if events_source is None:
            events_source = parent if isinstance(parent, Window) else \
                parent.window
        self.events_source = events_source
        self.modal_child = None
        if modal:
            self.events_source.modal_child = self

        self.child_need_organize = False
        self.child_need_resize = False

    def remove(self, w):
        super(Window, self).remove(w)
        if w is self.modal_child:
            self.modal_child = None

    def sorted_children(self):
        # Since the children can overlap in a window We define that
        # the last window added is on the top Maybe we need to have a
        # z sorting in the future...
        if self.modal_child:
            return [self.modal_child]
        return list(reversed(self.children))

    def resize(self):
        return

    def need_organize(self, child):
        self.child_need_organize = True

    def need_resize(self, child):
        self.child_need_resize = True

    def draw(self, painter):
        if self.modal_child is None:
            Widget.draw(self, painter)
        else:
            painter.move(self.modal_child.pos)
            self.modal_child.draw(painter)
            painter.umove(self.modal_child.pos)

    def tick(self):
        while self.child_need_resize:
            self.child_need_resize = False
            self.do_resize()
        while self.child_need_organize:
            self.child_need_organize = False
            self.do_organize()

        self.events = []
        if not self.modal_child:
            for e, v in self.events_source.events:
                if e == 'mouse-down':
                    if self.mouse_down(*v):
                        continue
                elif e == 'mouse-up':
                    if self.mouse_up(*v):
                        continue
                elif e == 'mouse-motion':
                    if self.mouse_motion(*v):
                        continue
                elif e == 'key-down':
                    if self.key_down(*v):
                        continue
                elif e == 'resized':
                    self.size = v[0]
                    self.resized = False
            for c in self.children:
                c.tick()
        else:
            self.events = self.events_source.events
            self.modal_child.tick()

        self.emit('tick')
