#    Tichy
#
#    copyright 2008 Guillaume Chereau (charlie@openmoko.org)
#
#    This file is part of Tichy.
#
#    Tichy is free software: you can redistribute it and/or modify it
#    under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Tichy is distributed in the hope that it will be useful, but
#    WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Tichy.  If not, see <http://www.gnu.org/licenses/>.

from .object import Object
from .item import Item

class Frame(object):
    """Define a frame from an image"""
    def __init__(self, image):
        self.image = image
    def __repr__(self):
        return "Frame(%s)" % self.image
    def draw(self, painter, size):
    	return painter.draw_frame(self, size)
    	
class Font(object):
    def __init__(self, file, size = 24):
        self.file = file
        self.size = size
        self.font = None
                
    def load(self, painter):
        if self.font:
            return
        self.font = painter.font_from_file(self.file, self.size)
        
    def render(self, painter, text, color = None, length = None):
        self.load(painter)
        return self.font.render(text, color, length)
        
    def resize(self, size):
        """Create a new font identical to this one but with a different size
        """
        return Font(self.file, size)

class Filter(object):
    """Filter condiction for sub-styles"""
    def __call__(self, w):
        raise NotImplementedError
        
class Tag(Filter):
    def __init__(self, name):
        self.name = name
    def __call__(self, w):
        return self.name in w.tags

class TypeFilter(Filter):
    """Filter on the widget type"""
    def __init__(self, type):
        self.type = type
    def __call__(self, w):
        return isinstance(w, self.type)
    def __repr__(self):
        return self.type.__name__
    def __cmp__(self, v):
        """We define the cmp method so that the more general rules are 'lower'
        than more 'specifics'
        """
        if isinstance(v, TypeFilter):
            if self.type == v.type: return 0
            if issubclass(self.type, v.type): return 1
            if issubclass(v.type, self.type): return -1
        return -1
        
class ItemTypeFilter(Filter):
    def __init__(self, type):
        self.type = type
    def __call__(self, w):
        return isinstance(w.item, self.type)

    	
class Style(dict, Item):
    """A Style is a dictionary of key -> values with parenting property

    Styles are usefull to give some properties to widgets that can be
    used by the Design service to know how to draw them.

    When you apply a style to a widget, you get the actual style
    dictionary that can be used by any painter to draw the wiget.

    Here are the rules :

    - first the style tries to get the attributes form the sub-styles

    - then it gets its own attributes

    - finally it gets the attributes from its parent style
    """
    def __init__(self, parent = None):
        super(Style, self).__init__()
        self.parent = parent
        self.parts = []

    # TODO: this is not really good, we shouldn't have to call this 
    @classmethod
    def create(cls):
        return cls.from_dict(None, cls.code())
        
    def add_part(self, filter, style):
        self.parts.append((filter, style))
        
    # XXX: also apply to Style attribute (children-style, etc..)
    def apply(self, widget, up = True):
        ret = {}
        if up and self.parent is not None:
            ret.update(self.parent.apply(widget))
        ret.update(self)
        for (f,p) in self.parts:
            assert isinstance(f, Filter)
            if f(widget):
                ret.update(p.apply(widget, up = False))
        return ret
        
    @classmethod
    def from_dict(cls, parent, d):
        from tichy import gui
        ret = cls(parent)
        for k, v in d.iteritems():
            if isinstance(k, str) and k.endswith('-style'):
                ret[k] = cls.from_dict(ret, v)
            elif isinstance(k, str):
                ret[k] = v
            elif isinstance(k, Filter):
                style = cls.from_dict(ret, v)
                ret.add_part(k, style)
            elif issubclass(k, gui.Widget):
                style = cls.from_dict(ret, v)
                ret.add_part(TypeFilter(k), style)
            elif issubclass(k, Item):
                style = cls.from_dict(ret, v)
                ret.add_part(ItemTypeFilter(k), style)
        # sort the parts do that the more general are at the beginning
        # at will be overriden by the more specific ones
        ret.parts = sorted(ret.parts)
        return ret

