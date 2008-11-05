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
from geo cimport Vect, Rect, c_Rect, c_rect_intersect, c_vect_equal, c_rect_to_py, c_rect_move

from geo import asvect

cimport painter
from painter cimport Painter

cdef class Widget(Object):
    """Base class for all the widgets
    
        This is really similar to gtk.widget, except lighter.
    """
    def __init__(self, Widget parent, style = None, Vect optimal_size = None, Vect min_size = None,
                 int expand = False, item = None, Widget same_as = None, 
                 tags = None, Vect pos = None, **kargs):
        super(Widget, self).__init__()
        self.children = []
        self.item = item
        self.tags = tags or []
        parent = parent.get_contents_child() if parent else None
        self.parent = parent
        
        self.resizable = optimal_size is None
        
        self._optimal_size = optimal_size or Vect(0,0)
        self._min_size = min_size
        self.expand = expand
        
        self._organized = False
        
        self.rect = Rect(Vect(0,0), self.optimal_size)
        self._pos = pos or Vect(0,0)
        self.focused = None
        self.clickable = False
        self.surface = None     # This is used for the widget that keep a copy of there surface for optimisation
        self.store_surface = False   # Set to true for the widget to keep a memory of it own surface
        
        if same_as is None:
            self.style = style
        else:
            self._style = same_as._style
            self.style_dict = same_as.style_dict
            
        self.fixed_optimal_size = optimal_size is not None
        self.fixed_min_size = min_size is not None or 'min-size' in self.style_dict
        
        if parent:
            parent.add(self)
        
    def get_contents_child(self):
        return self
       
    property style: 
        def __get__(self):
            return self._style
        def __set__(self, style):
            if style:
                self._style = style
            else:
                if 'children-style' in self.parent.style_dict:
                    self._style = self.parent.style_dict['children-style']
                else:
                    self._style = self.parent.style
            self.style_dict = self._style.apply(self)
            children_style = self._style if 'children-style' not in self.style_dict else  self.style_dict['children-style']
            for c in self.children:
                c.style = children_style
            self.c_need_redraw(&self.rect.c_value)
            
    def get_style_dict(self):
        cdef dict ret = self.style_dict
        return ret
        
    def add_tag(self, tag):
        if tag in self.tags:
            return
        self.tags.append(tag)
        self.style = self.style
    def remove_tag(self, tag):
        if not tag in self.tags:
            return
        self.tags.remove(tag)
        self.style = self.style
    
    property size:
        def __get__(self):
            return self.rect.size
        def __set__(self, Vect value):
            if c_vect_equal(&self.rect.c_value.size, &value.c_value):
                return
            self.rect.c_value.size = value.c_value
            self.organized = False
            
    property pos:
        def __get__(self):
            return self._pos
        def __set__(self, Vect pos):
            if c_vect_equal(&pos.c_value, &self._pos.c_value):
                return
            self._pos = pos
            self.need_redraw(self.rect) # XXX: slow
            
    property min_size:
        def __get__(self):
            return self._min_size or self.style_dict.get('min-size', Vect(0,0))
        def __set__(self, Vect value):
            self._min_size = value
            
    property optimal_size:
        def __get__(self):
            return self._optimal_size
        def __set__(self, Vect value):
            self._optimal_size = value
            self.parent.resized = False
            self.parent.organized = False

    property contents_rect:
        def __get__(self):
            return self.rect
            
    property contents_pos:
        def __get__(self):
            return self.contents_rect.pos
    
    property contents_size:
        def __get__(self):
            return self.contents_rect.size
    
    property organized:
        def __get__(self):
            return self._organized
        def __set__(self, int value):
            self._organized = value
            if not value:
                self.need_organize(self)
                
    cdef void c_need_organize(self, Widget child):
        if self.parent is not None:
            self.parent.need_organize(child) # XXX: super slow !!! Need to make screen cython
    def need_organize(self, Widget child):
        self.c_need_organize(child)
            
    property resized:
        def __get__(self):
            return self._resized or not self.resizable
        def __set__(self, int value):
            self._resized = value
            if not value:
                self.need_resize(self)
            
    cdef void c_need_resize(self, Widget child):
        if self.parent is not None:
            self.parent.need_resize(child) # XXX: super slow !!! Need to make screen cython
    def need_resize(self, Widget child):
        self.c_need_resize(child)
    
    def __get_window(self):
        from window import Window
        if isinstance(self.parent, Window):
            return self.parent
        return self.parent.window
    window = property(__get_window)
    
    def __get_screen(self):
        return self.parent.screen
    screen = property(__get_screen)
    
    def set_rect(self, Rect r):
        # TODO: use a virtual attribute 
        self.rect = r
        self.organized = False
    
    # TODO: make it faster using cdef
    def abs_pos(self):
        """Return the position of the widget relative to its window"""
        if self.window is self.parent:
            return self.pos
        return self.pos + self.parent.abs_pos()
    def screen_pos(self):
        if self.screen is self.parent:
            return self.pos
        return self.pos + self.parent.screen_pos()
        
    def parent_as(self, cls):
        if not self.parent:
            return None
        if isinstance(self.parent, cls):
            return self.parent
        return self.parent.parent_as(cls)
        
    def focus_child(self, Widget w):
        self.focused = w
        
    def add(self, Widget w):
        """Add a child to the widget"""
        self.children.append(w)
        self._emit_1('add-child', w)    # XXX: remove ?
        self.resized = False
        self.organized = False
        
    def remove(self, Widget w):
        self.children.remove(w)
        self.organized = False
        self.resized = False
        self.need_redraw(self.rect)
        
    def destroy(self):
        if not self.parent: # Just to ensure we are not already destroyed
            return
        self.parent.remove(self)
        self.parent = None
        self._emit('destroyed')
        cdef Widget c
        for c in self.children[:]:
            c.destroy()
        
    cdef void c_need_redraw(self, c_Rect *rect):
        self.surface = None
        cdef c_Rect p_rect
        c_rect_move(rect, &self._pos.c_value, &p_rect)
        if self.parent is not None:
            self.parent.need_redraw(c_rect_to_py(&p_rect)) # XXX: super slow !!! Need to make screen cython
    def need_redraw(self, Rect rect):
        self.c_need_redraw(&rect.c_value)
        
    cdef void c_draw(self, Painter painter) except *:
        """Draw the widget on a painter object
        
            Ths position where we paint is stored in the painter itself (opengl style) 
        """ 
        if self.store_surface and self.surface is None:
            surface = painter.c_surface_from_size(&self.rect.c_value.size)
            self.store_surface = False
            self.c_draw(painter._to_surface(surface))
            self.store_surface = True
            self.surface = surface
        
        if self.surface is not None:
            painter._draw_surface(self.surface, None)
            return
        painter._draw(self)
        
        cdef c_Rect mask
        cdef Widget c
        for c in self.children:
            painter.c_move(&c._pos.c_value)
            mask = painter.c_mask
            painter.c_clip(&c.rect.c_value)
            if c_rect_intersect(&painter.c_mask, &c.rect.c_value):
                c.c_draw(painter)
            painter.c_set_mask(&mask)
            painter.c_umove(&c._pos.c_value)
            
    def draw(self, o):
        self.c_draw(o)
        
    cdef void c_do_resize(self) except *:
        cdef Widget c
        for c in self.children:
            c.c_do_resize()
        if self._resized:
            return
        self.resize()
        self._resized = True
    def do_resize(self):
        self.c_do_resize()
        
    def resize(self):
        if not self.fixed_min_size:
            self.min_size = Vect.merge(Vect(0,0), *[c.optimal_size for c in self.children])
        if not self.fixed_optimal_size:
            self.optimal_size = Vect.merge(self.min_size, *[c.optimal_size for c in self.children])
        
    def do_organize(self):
        if not self.organized:
            self.organize()
            self.need_redraw(self.rect)
        for c in self.children:
            c.do_organize()
        self.organized = True
            
    def organize(self):
        """Set all children size and position"""
        cdef Widget c
        for c in self.children:
            c.size = self.contents_size
            c.pos = self.contents_pos
            
    def sorted_children(self):
        """Return the children, sorted with the one on top first"""
        # For the moment I suppose that none of the children overlap, so we don't sort anything
        return self.children
            
    def mouse_down(self, Vect pos):
        cdef Widget c
        cdef Vect cpos
        
        for c in self.sorted_children():
            cpos = pos - c.pos
            if not cpos in c.rect:
                continue
            if c.mouse_down(cpos):
                self.focused = c
                return True
        if self.clickable:
            self._emit_1('mouse-down', pos)
            return True
        return False
        
    def mouse_down_cancel(self):
        """Cancel the last mouse down event
        
            This function is mainly used for scrollable area, where we don't know from the beginning
            if we are clicking a widget, or just moving the area. """
        if self.focused:
            self.focused.mouse_down_cancel()
            self.focused = None
        
    def mouse_up(self, Vect pos):
        if not self.focused:
            self._emit_1('mouse-up', pos)
            return True
        else:
            ret = self.focused.mouse_up(pos - self.focused.pos)
            self.focused = None
            return ret
        
    def mouse_motion(self, Vect pos):
        if not self.focused:
            self._emit_1('mouse-motion', pos)
        else:
            self.focused.mouse_motion(pos - self.focused.pos)
            
    def key_down(self, key):
        for c in self.sorted_children():
            if c.key_down(key):
                return True
        return False
            
    def tick(self):
        """This is only used for windows widgets"""
        for c in self.children:
            c.tick()
