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
from geo import Vect, asvect

class ImageWidget(Widget):
    def __init__(self, parent, image, **kargs):
        self.image = image
        size = asvect(image.size) if image.size else None
        super(ImageWidget, self).__init__(parent, item=image,
                                          optimal_size=size, min_size=size,
                                          **kargs)
        self.connection = image.connect('modified', self.on_image_modified)
    
    def draw(self, painter):
        self.image.load(painter)
        painter.draw_surface(self.image.surf)
    
    def on_image_modified(self, image):
        self.need_redraw(self.rect)
        
    def destroy(self):
        # Very important, cause otherwise the image keep having a
        # reference to the view
        self.item.disconnect(self.connection)
        super(ImageWidget, self).destroy()
