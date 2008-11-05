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
from geo cimport Vect

cimport painter
from painter cimport Painter

cimport widget
from widget cimport Widget

cdef class SdlPainter(Painter):
    cdef public object surface
    cdef public object font
    
    cdef void _draw_widget(self, Widget w)
    cdef void _draw_label(self, Widget w)
    cdef void _draw_frame(self, frame, Vect size)
