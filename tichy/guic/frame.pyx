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
from geo cimport Vect, Rect

cdef class Frame(Widget):
    def __init__(self, parent, border = -1, **kargs):
        self.__border = border
        super(Frame, self).__init__(parent, **kargs)
        
    def __get_contents_rect(self):
        cdef int border = self.border
        return Rect(self.rect.pos + Vect(border, border), self.rect.size - Vect(border, border) * 2)
    contents_rect = property(__get_contents_rect)

    property border:
        def __get__(self):
            return self.__border if self.__border != -1 else self.style_dict.get('border', 0)
        def __set__(self, value):
            self.__border = value
    
