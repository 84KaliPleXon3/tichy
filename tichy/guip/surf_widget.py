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
import pygame

class SurfWidget(Widget):
    def __init__(self, parent, size, **kargs):
        super(SurfWidget, self).__init__(parent, optimal_size = size, **kargs)
        self.store_surface = True
        self.surface = pygame.Surface(size, 0, 32).convert()
        
    def resize(self):
        pass
        
    def need_redraw(self, rect):
        if self.parent is not None:
            self.parent.need_redraw(rect.move(self.pos))
        
    def draw(self, painter):
        assert self.surface
        painter.draw_surface(self.surface)
        # Widget.draw(self, painter)
