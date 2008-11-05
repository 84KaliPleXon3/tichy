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

cdef struct c_Vect:
    int x
    int y

cdef class Vect:
    cdef c_Vect c_value
    
cdef Vect c_vect_to_py(c_Vect* v)
cdef inline int c_vect_equal(c_Vect* v1, c_Vect* v2)

cdef struct c_Rect:
    c_Vect pos
    c_Vect size

cdef class Rect:
    cdef c_Rect c_value
    
    cpdef Rect move(self, Vect pos)

    cpdef Rect clip(self, Rect r)
    cpdef Rect merge(self, Rect r)
    cpdef int intersect(self, Rect r)
    cpdef Rect inside(self, Rect r)

cdef Rect c_rect_to_py(c_Rect *r)

cdef inline int c_rect_left(c_Rect *r)
cdef inline int c_rect_right(c_Rect *r)
cdef inline int c_rect_top(c_Rect *r)
cdef inline int c_rect_bottom(c_Rect *r)
cdef inline int c_rect_width(c_Rect *r)
cdef inline int c_rect_height(c_Rect *r)

cdef int c_rect_contains(c_Rect *r, c_Vect *v)
cdef int c_rect_intersect(c_Rect *r1, c_Rect *r2)
cdef void c_rect_inside(c_Rect *r1, c_Rect *r2, c_Rect *ret)
cdef void c_rect_merge(c_Rect *r1, c_Rect *r2, c_Rect *ret)
cdef void c_rect_clip(c_Rect *r1, c_Rect *r2, c_Rect *ret)

cdef inline void c_rect_move(c_Rect *r, c_Vect *v, c_Rect *ret)
