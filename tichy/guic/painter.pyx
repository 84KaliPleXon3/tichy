

cimport geo
from geo cimport Vect, Rect, c_Vect, c_Rect, c_vect_to_py, c_rect_to_py, c_rect_clip
from geo import asvect, asrect

from label import Label

cdef class Painter:
    """ This class is used to draw all the widgets
        
        Te idea is to subclass it when we want special drawing style.
    """
    
    def __init__(self, Vect pos, Rect mask):
        self.c_pos = pos.c_value
        self.c_mask = mask.c_value
        
    property pos:
        def __get__(self): return c_vect_to_py(&self.c_pos)
    property mask:
        def __get__(self): return c_rect_to_py(&self.c_mask)

    cdef void c_move(self, c_Vect *v):
        self.c_pos.x += v.x; self.c_pos.y += v.y
        self.c_mask.pos.x -= v.x; self.c_mask.pos.y -= v.y
    def move(self, Vect v): self.c_move(&v.c_value)
        
    cdef void c_umove(self, c_Vect *v):
        self.c_pos.x -= v.x; self.c_pos.y -= v.y
        self.c_mask.pos.x += v.x; self.c_mask.pos.y += v.y
    def umove(self, Vect v): self.c_umove(&v.c_value)
        
    cdef void c_clip(self, c_Rect *r):
        cdef c_Rect mask
        c_rect_clip(&self.c_mask, r, &mask)
        self.c_set_mask(&mask)
    def clip(self, Rect r): self.c_clip(&r.c_value)
        
    cdef void c_set_mask(self, c_Rect *r):
        self.c_mask = r[0]
    def set_mask(self, Rect r): self.c_set_mask(&r.c_value)
        
    cdef Painter _to_surface(self, surf):
        raise NotImplementedError
            
    cdef void _draw(self, o):
        raise NotImplementedError
        
    cdef c_surface_from_size(self, c_Vect *size):
        raise NotImplementedError
    def surface_from_size(self, Vect v):
        self.c_surface_from_size(&v.c_value)
        
    cdef _surface_from_image(self, char* path):
        raise NotImplementedError
        
    cdef _surface_from_text(self, font, text, color, length):
        """Create a new surface from a text"""
        raise NotImplementedError
    
    cdef void _draw_surface(self, surf, area):
        raise NotImplementedError
    def draw_surface(self, surf, area = None): self._draw_surface(surf, area)
    
    cdef void _fill(self, color, Vect size):
        raise NotImplementedError
    def fill(self, color, size): self._fill(color, asvect(size))

    cdef void _draw_frame(self, frame, Vect size):
        raise NotImplementedError
    def draw_frame(self, frame, size): self._draw_frame(frame, asvect(size))
            
    cdef void _flip(self, Rect rect):
        pass
    def flip(self, r): self._flip(asrect(r))
    
