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


from widget import Widget
from geo import Vect, Rect
from window import Window


class Screen(Window):
    """Main widget for everything

    Screen is the widget that is at the end of the chain when we emit
    "need-redraw".  It is the only widget that start a redrawing
    sequence.  It may seem not optimized to always redraw from the top
    widget, but the idea is that you can then have transparency in any
    widgets
    """

    def __init__(self, events_source, painter, **kargs):
        self.redraw_rect = None
        super(Screen, self).__init__(None, events_source=events_source,
                                     modal=False, **kargs)
        self.size = Vect(480, 640) # TODO find a better way
        self.painter = painter
        self.redraw_rect = self.rect

        self.monitor(events_source, 'tick', self.on_tick)

    screen = property(lambda self: self)

    def draw(self):
        if not self.redraw_rect:
            return
        assert self.painter.pos.x == self.painter.pos.y == 0
        # TODO: use virtual attribute
        self.painter.set_mask(self.redraw_rect)
        # The background color
        self.painter.fill((0, 0, 0), self.size)
        super(Screen, self).draw(self.painter)
        self.painter.flip(self.redraw_rect)
        self.redraw_rect = None

    def need_redraw(self, rect):
        self.redraw_rect = rect if not self.redraw_rect else \
            self.redraw_rect.merge(rect)

    def on_tick(self, event_source):
        self.tick()

    def tick(self):
        self.draw()
        super(Screen, self).tick()

    def destroy(self):
        super(Screen, self).destroy()
        import pygame.display
        pygame.display.quit()
