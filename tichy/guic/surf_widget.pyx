
cimport geo
from geo cimport c_Rect, c_rect_to_py, c_rect_move

cimport widget
from widget cimport Widget

cimport painter
from painter cimport Painter

import pygame

cdef class SurfWidget(Widget):
    def __init__(self, parent, size, **kargs):
        super(SurfWidget, self).__init__(parent, optimal_size = size, **kargs)
        self.store_surface = True
        self.surface = pygame.Surface(size, 0, 32)
        
    cdef void c_do_resize(self):
        pass
        
    cdef void c_need_redraw(self, c_Rect *rect):
        cdef c_Rect p_rect
        c_rect_move(rect, &self._pos.c_value, &p_rect)
        if self.parent is not None:
            self.parent.need_redraw(c_rect_to_py(&p_rect)) # XXX: super slow !!! Need to make screen cython
