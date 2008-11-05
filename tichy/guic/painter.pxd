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

cimport geo
from geo cimport Vect, Rect, c_Vect, c_Rect


cdef class Painter:
    """ This class is used to draw all the widgets
        
        Te idea is to subclass it when we want special drawing style.
    """
    cdef c_Vect c_pos
    cdef c_Rect c_mask
    
    cdef void _draw(self, o)
    
    cdef void c_move(self, c_Vect *v)
    cdef void c_umove(self, c_Vect *v)
    
    cdef void c_clip(self, c_Rect *r)
    cdef void c_set_mask(self, c_Rect *r)
    
    cdef Painter _to_surface(self, surf)
    cdef c_surface_from_size(self, c_Vect *size)
    cdef _surface_from_image(self, char* path)
    cdef _surface_from_text(self, font, text, color, length)
    cdef void _draw_surface(self, surf, area)
    cdef void _fill(self, color, Vect size)
    cdef void _draw_frame(self, frame, Vect size)
    cdef void _flip(self, Rect r)

