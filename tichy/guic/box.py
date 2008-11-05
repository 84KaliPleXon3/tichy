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


from widget import Widget
from frame import Frame
from geo import Vect, Rect

class Box(Frame):
    """ Box layout widget, similar to gtk boxes
    
        This widget can be used to organize widgets into space
    """
    def __init__(self, parent, axis = 0, spacing = None, **kargs):
        self.axis = axis
        self.__spacing = spacing
        super(Box, self).__init__(parent, **kargs)
        
    def __get_spacing(self):
        return self.__spacing if self.__spacing is not None else self.style_dict.get('spacing', 0)
    def __set_spacing(self, value):
        self.__spacing = value
    spacing = property(__get_spacing, __set_spacing)
        
    def resize(self):
        axis = self.axis
        optimal_size = Vect(0,0)
        min_size = Vect(0,0)
        if self.children:
            min_size = min_size.set(axis, sum(c.min_size[axis] for c in self.children))
            min_size = min_size.set(axis - 1, max(c.min_size[axis - 1] for c in self.children))
        
            optimal_size = optimal_size.set(axis, sum(c.optimal_size[axis] + self.spacing for c in self.children) - self.spacing)
            optimal_size = optimal_size.set(axis - 1, max(c.optimal_size[axis - 1] for c in self.children))
            optimal_size += Vect(self.border, self.border) * 2

        self.min_size = min_size
        self.optimal_size = optimal_size
    
    def organize(self):
        axis = self.axis
        # First we put all the children in there minimum size
        for c in self.children:
            c.size = c.min_size.set(axis - 1, self.contents_size[axis - 1])
            assert c.size[axis] >= c.min_size[axis]

        # We grow the children as much as we can
        length = self.contents_size[axis]
        while True:
            children_need =  [c for c in self.children if c.optimal_size[axis] > c.size[axis]]
            if not children_need:
                break
                
            tot = sum((c.size[axis] + self.spacing for c in self.children)) - self.spacing
            free = max(0, length - tot)
                
            free_per_child = free / len(children_need)
            for c in children_need:
                if c.optimal_size[axis] - c.size[axis] < free_per_child:
                    c.size = c.size.set(axis, c.optimal_size[axis])
                    break
            else:
                break
        for c in children_need:
            c.size = c.size.set(axis, c.size[axis] + free_per_child)
                
        # If we still have some free space, we grow the expand children
        tot = sum((c.size[axis] + self.spacing for c in self.children)) - self.spacing
        free = length - tot
        if free > 0:
            nb_expand = sum(1 for c in self.children if c.expand)
            if nb_expand:
                for c in self.children:
                    if not c.expand:
                        continue
                    given = free / nb_expand
                    assert given >= 0
                    c.size = c.size.set(axis, c.size[axis] + given)
            
        # Finally we also set the positions 
        pos = self.contents_pos
        for c in self.children:
            assert c.size[axis] >= c.min_size[axis], (c, c.size[axis], c.min_size[axis])
            c.pos = pos
            pos += Vect(c.size[0] + self.spacing if axis == 0 else 0, c.size[1] + self.spacing if axis == 1 else 0 )
            
        
class Fixed(Widget):
    def __init__(self, parent, **kargs):
        super(Fixed, self).__init__(parent, **kargs)
    def organize(self):
        for c in self.children:
            c.size = c.optimal_size
            c.do_organize()
        
            

