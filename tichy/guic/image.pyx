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

cimport widget
from widget cimport Widget

cimport geo
from geo cimport Vect

from geo import asvect

cimport painter
from painter cimport Painter


cdef class ImageWidget(Widget):
    cdef object image
    cdef object connection
    
    def __init__(self, Widget parent, object image, **kargs):
        self.image = image
        size = asvect(image.size) if image.size else None
        super(ImageWidget, self).__init__(parent, item=image, optimal_size=size, min_size=size, **kargs)
        self.connection = image.connect('modified', self.on_image_modified)
        
    cdef void c_draw(self, Painter painter):
        self.image.load(painter)
        painter._draw_surface(self.image.surf, None)
        
    def on_image_modified(self, image):
        self.need_redraw(self.rect)
    
    def destroy(self):
        super(ImageWidget, self).destroy()



        
