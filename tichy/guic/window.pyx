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

cimport widget
from widget cimport Widget

cimport painter
from painter cimport Painter

cimport geo
from geo cimport Vect

cdef class Window(Widget):
    """ Special widget that can receive events from an external source
        
        A window can also be an event source for other sub window. We can also block the events to all but one
        child, making it a modal dialog.
    """
    
    cdef readonly list events
    cdef object events_source
    cdef Window modal_child
    cdef int modal
    
    cdef int child_need_organize
    cdef int child_need_resize

    def __init__(self, Widget parent, modal = True, events_source = None, **kargs):
        Widget.__init__(self, parent, **kargs)
        
        if events_source is None:
            events_source = parent if isinstance(parent, Window) else parent.window
            
        self.events_source = events_source
        self.modal_child = None

        cdef Window source
        if modal and isinstance(self.events_source, Window):
            source = self.events_source
            source.modal_child = self
            
        self.child_need_organize = False
        self.child_need_resize = False

    def remove(self, Widget w):
        super(Window, self).remove(w)
        if w is self.modal_child:
            self.modal_child = None
            
    def resize(self):
        return
        
    def sorted_children(self):
        if self.modal_child:
            return [self.modal_child]
        return list(reversed(self.children))
        
    cdef void c_draw(self, Painter painter):
        if self.modal_child is None:
            Widget.c_draw(self, painter)
        else:
            painter.c_move(&self.modal_child._pos.c_value)
            self.modal_child.c_draw(painter)
            painter.c_umove(&self.modal_child._pos.c_value)
            
    def need_organize(self, child):
        self.child_need_organize = True
    def need_resize(self, child):
        self.child_need_resize = True
            
    def tick(self):
        if self.child_need_resize:
            self.do_resize()
            self.child_need_resize = False
        if self.child_need_organize:
            self.do_organize()
            self.child_need_organize = False
        
        self.events = []
        if self.modal_child is None:
            for e,v in self.events_source.events:
                if e == 'mouse-down':
                    if self.mouse_down(v[0]): continue
                if e == 'mouse-up':
                    if self.mouse_up(v[0]): continue
                if e == 'mouse-motion':
                    if self.mouse_motion(v[0]): continue
                if e == 'key-down':
                    if self.key_down(*v): continue
                if e == 'resized':
                    self.size = v[0]
                    self.resized = False
                    continue
            for c in self.children:
                c.tick()
        else:
            self.events = self.events_source.events
            self.modal_child.tick()
        self._emit('tick')
