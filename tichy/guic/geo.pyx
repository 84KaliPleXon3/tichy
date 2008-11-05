

cdef class Vect:
    def __init__(self, int x, int y):
        self.c_value.x = x
        self.c_value.y = y
        
    property x:
        def __get__(self): return self.c_value.x
        def __set__(self, int value): self.c_value.x = value
    property y:
        def __get__(self): return self.c_value.y
        def __set__(self, int value): self.c_value.y = value    
    
        
    def to_list(self):
        return (self.x, self.y)
        
    def __len__(self): return 2
        
    def __repr__(self):
        return repr((self.x, self.y))
    
    def __getitem__(self, int index):
        if index == 0:
            return self.c_value.x
        else:
            return self.c_value.y
            
    def __iter__(Vect self):
        return iter((self.x, self.y))
            
    def __add__(Vect self, Vect v):
        return Vect(self.c_value.x + v.c_value.x, self.c_value.y + v.c_value.y)
        
    def __sub__(Vect self, Vect v):
        return Vect(self.c_value.x - v.c_value.x, self.c_value.y - v.c_value.y)
        
    def __neg__(Vect self):
        return Vect(-self.c_value.x, -self.c_value.y)
        
    def __mul__(Vect self, int k):
        return Vect(self.c_value.x * k, self.c_value.y * k)
        
    def __div__(Vect self, int k):
        return Vect(self.c_value.x / k, self.c_value.y / k)
    
    def set(Vect self, int index, int value):
        return Vect( value if index == 0 else self.c_value.x, self.c_value.y if index == 0 else value)
        
    def merge(v, *vs):
        vs = (v,) + vs
        cdef int x = 0
        cdef int y = 0
        cdef Vect vect
        for vect in vs:
            x,y = max(x, vect.c_value.x), max(y, vect.c_value.y)
        return Vect(x,y)
        
cdef Vect c_vect_to_py(c_Vect* v):
    return Vect(v.x, v.y)
    
cdef inline int c_vect_equal(c_Vect* v1, c_Vect* v2):
    return v1.x == v2.x and v1.y == v2.y
        
cdef class Rect:
    def __init__(self, pos, size):
        self.pos = Vect(pos[0], pos[1])
        self.size = Vect(size[0], size[1])
        
    property pos:
        def __get__(self): return c_vect_to_py(&self.c_value.pos)
        def __set__(self, Vect value): self.c_value.pos = value.c_value
    property size:
        def __get__(self): return c_vect_to_py(&self.c_value.size)
        def __set__(self, Vect value): self.c_value.size = value.c_value
        
    def __repr__(self):
        return repr((self.pos, self.size))
        
    def __getitem__(self, int index):
        if index == 0:
            return self.pos
        else:
            return self.size
            
    def __iter__(self):
        return iter((self.pos, self._size))
        
    def to_list(self):
        return (self.c_value.pos.x, self.c_value.pos.y, self.c_value.size.x, self.c_value.size.y)

    cpdef Rect move(self, Vect pos):
        return Rect(self.pos + pos, self.size)
        
    def moveto(self, pos):
        return Rect(pos, self._size)
        
    def resize(self, size):
        return Rect(self.pos, size)
        
    def is_empty(self):
        return self.size.x == self.size.y == 0
        
    def __contains__(self, Vect v):
        return c_rect_contains(&self.c_value, &v.c_value)
        
    cpdef Rect clip(self, Rect r):
        cdef c_Rect ret
        c_rect_clip(&self.c_value, &r.c_value, &ret)
        return c_rect_to_py(&ret)
        
    cpdef Rect merge(self, Rect r):
        cdef c_Rect ret
        c_rect_merge(&self.c_value, &r.c_value, &ret)
        return c_rect_to_py(&ret)
        
    cpdef int intersect(self, Rect r):
        return c_rect_intersect(&self.c_value, &r.c_value)
               
    cpdef Rect inside(self, Rect r):
        """Return a rect of the same size put inside the rect r"""
        cdef c_Rect ret
        c_rect_inside(&self.c_value, &r.c_value, &ret)
        return c_rect_to_py(&ret)

cdef Rect c_rect_to_py(c_Rect *r):
    return Rect((r.pos.x, r.pos.y), (r.size.x, r.size.y))
        
cdef inline int c_rect_left(c_Rect *r): return r.pos.x
cdef inline int c_rect_right(c_Rect *r): return r.pos.x + r.size.x
cdef inline int c_rect_top(c_Rect *r): return r.pos.y
cdef inline int c_rect_bottom(c_Rect *r): return r.pos.y + r.size.y
cdef inline int c_rect_width(c_Rect *r): return r.size.x
cdef inline int c_rect_height(c_Rect *r): return r.size.y


cdef int c_rect_contains(c_Rect *r, c_Vect *v):
    return v.x >= c_rect_left(r) and v.y >= c_rect_top(r) and \
                v.x < c_rect_right(r) and v.y < c_rect_bottom(r)

cdef int c_rect_intersect(c_Rect *r1, c_Rect *r2):
    return c_rect_left(r1) <= c_rect_right(r2) and c_rect_right(r1) > c_rect_left(r2) and \
               c_rect_top(r1) <= c_rect_bottom(r2) and c_rect_bottom(r1) > c_rect_top(r2)     
               
cdef void c_rect_inside(c_Rect *r1, c_Rect *r2, c_Rect *ret):
    cdef int width = min(c_rect_width(r1), c_rect_width(r2))
    cdef int height = min(c_rect_height(r1), c_rect_height(r2))
    cdef int left = max(c_rect_left(r1), c_rect_left(r2))
    cdef int top = max(c_rect_top(r1), c_rect_top(r2))
    ret.pos.x = left; ret.pos.y = top
    ret.size.x = width; ret.size.y = height
    
cdef void c_rect_merge(c_Rect *r1, c_Rect *r2, c_Rect *ret):
    cdef int left = min(c_rect_left(r1), c_rect_left(r2))
    cdef int right = max(c_rect_right(r1), c_rect_right(r2))
    cdef int top = min(c_rect_top(r1), c_rect_top(r2))
    cdef int bottom = max(c_rect_bottom(r1), c_rect_bottom(r2))
    ret.pos.x = left; ret.pos.y = top
    ret.size.x = right - left; ret.size.y = bottom - top
    
cdef void c_rect_clip(c_Rect *r1, c_Rect *r2, c_Rect *ret):
    cdef int left = max(c_rect_left(r1), c_rect_left(r2))
    cdef int right = min(c_rect_right(r1), c_rect_right(r2))
    cdef int top = max(c_rect_top(r1), c_rect_top(r2))
    cdef int bottom = min(c_rect_bottom(r1), c_rect_bottom(r2))
    right = max(right, left)
    bottom = max(bottom, top)
    ret.pos.x = left; ret.pos.y = top
    ret.size.x = right - left; ret.size.y = bottom - top
    
cdef inline void c_rect_move(c_Rect *r, c_Vect *v, c_Rect *ret):
    ret.pos.x = r.pos.x + v.x
    ret.pos.y = r.pos.y + v.y
    ret.size.x = r.size.x
    ret.size.y = r.size.y

def asvect(o):
    if isinstance(o, Vect):
        return o
    return Vect(o[0], o[1])
    
def asrect(o):
    if isinstance(o, Rect):
        return o
    if len(o) == 2:
        return Rect(o[0], o[1])
    if len(o) == 4:
        return Rect(o[0:2],o[2:4])

