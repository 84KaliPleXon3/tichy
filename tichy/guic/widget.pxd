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

cimport cobject
from cobject cimport Object

cimport geo
from geo cimport Vect, Rect, c_Rect

cimport painter
from painter cimport Painter

# XXX: the names of the attributes are totally crazy !!!

cdef class Widget(Object):
    cdef readonly Rect rect
    cdef readonly Vect _pos
    cdef readonly Widget parent
    cdef public item
    
    # cpdef Widget get_contents_child(self)
    cdef public list tags
    
    cdef public object surface
    cdef public int store_surface
    
    cdef public object _style
    cdef public dict style_dict
    
    # cpdef dict get_style_dict(self)
    
    cdef readonly Vect _optimal_size
    cdef public int fixed_optimal_size
    cdef readonly Vect _min_size
    cdef public int fixed_min_size
    cdef public int expand
    
    cdef public int _organized = False
    cdef void c_need_organize(self, Widget child)
    cdef public int _resized = False
    cdef void c_need_resize(self, Widget child)
    cdef public int resizable
    
    cdef public list children
    cdef readonly Widget focused
    cdef public int clickable
    
    cdef void c_draw(self, Painter painter) except *
    cdef void c_do_resize(self) except *

    cdef void c_need_redraw(self, c_Rect *rect)  

