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

from geo import Vect, Rect, asvect
from tichy.tasklet import Tasklet, Wait
from tichy.object import Object


class Widget(Object):
    """Base class for all the widgets

    This is really similar to gtk.widget, except lighter.
    """

    def __init__(self, parent, style=None, optimal_size=None,
                 min_size=None, expand=False, item=None,
                 same_as=None, tags=[], pos=None, **kargs):
        """Create a new Widget

        parameters:

        - parent The parent widget where we put this widget

        - style The style associated with this widget The style is not
          compulsory, it is only something that can be used by the
          Design

        - optimal_size The size requested for the widget

        - min_size The minimum size requested for the widget

        - expand If true the widget will try to take all the place it
          can

        - item What is the item associated with this widget (None if
          not) This is only used for the style rules

        - same_as This can be used to pass an other widget instance
          that we know has the same style than this one It is only
          used for optimazation when we want to show a huge number of
          similar widgets

        - tags A list of string, Can be used by the style rules
        """
        super(Widget, self).__init__()
        self.children = []
        self.item = item    # Set to None if the object is not a view
                            # on an item
        parent = parent.get_contents_child() if parent else None
        self.parent = parent

        self.style_dict = {}

        self.tags = set(tags)

        self.fixed_optimal_size = optimal_size is not None

        self.__optimal_size = optimal_size or Vect(0, 0)
        self.__min_size = min_size
        self.expand = expand

        self.__organized = False
        self.__resized = False

        self.rect = Rect((0, 0), min_size or Vect(0, 0))
        self.__pos = pos or Vect(0, 0)
        if same_as is None:
            self.style = style
        else:
            self.__style = same_as.__style
            self.style_dict = same_as.style_dict

        self.fixed_min_size = min_size is not None or \
            'min-size' in self.style_dict

        self.focused = None
        self.clickable = False
        self.surface = None     # This is used for the widget that
                                # keep a copy of there surface for
                                # optimisation
        self.store_surface = False   # Set to true for the widget to
                                     # keep a memory of it own surface

        if parent:
            parent.add(self)

    def get_contents_child(self):
        return self

    def __get_style(self):
        return self.__style

    def __set_style(self, style):
        if style:
            self.__style = style
        elif self.parent:
            if 'children-style' in self.parent.style_dict:
                self.__style = self.parent.style_dict['children-style']
            else:
                self.__style = self.parent.style
        self.style_dict = self.__style.apply(self)
        children_style = self.__style if \
            'children-style' not in self.style_dict else \
            self.style_dict['children-style']
        for c in self.children:
            c.style = children_style
        self.need_redraw(self.rect)
    style = property(__get_style, __set_style)

    def get_style_dict(self):
        # TODO: remove this ?
        ret = self.style_dict
        return ret

    def add_tag(self, tag):
        self.tags.add(tag)
        self.style = self.style

    def remove_tag(self, tag):
        self.tags.discard(tag)
        self.style = self.style

    def __get_min_size(self):
        return self.__min_size or self.style_dict.get('min-size', Vect(0, 0))

    def __set_min_size(self, value):
        self.__min_size = value

    min_size = property(__get_min_size, __set_min_size)

    def __get_optimal_size(self):
        return self.__optimal_size

    def __set_optimal_size(self, value):
        assert isinstance(value, Vect), value
        self.__optimal_size = value
        self.parent.resized = False
        self.parent.organized = False

    optimal_size = property(__get_optimal_size, __set_optimal_size)

    def __get_organized(self):
        return self.__organized

    def __set_organized(self, value):
        self.__organized = value
        if not value:
            self.need_organize(self)

    organized = property(__get_organized, __set_organized)

    def need_organize(self, child):
        if self.parent:
            self.parent.need_organize(child)

    def __get_resized(self):
        return self.__resized

    def __set_resized(self, value):
        self.__resized = value
        self.need_resize(self)
    resized = property(__get_resized, __set_resized)

    def need_resize(self, child):
        if self.parent:
            self.parent.need_resize(child)

    def __get_size(self):
        return self.rect.size

    def __set_size(self, value):
        if value == self.size:
            return
        self.rect = Rect(self.rect.pos, value)
        self.organized = False
    size = property(__get_size, __set_size)

    def __get_pos(self):
        return self.__pos

    def __set_pos(self, value):
        if value == self.__pos:
            return
        self.need_redraw(self.rect)
        self.__pos = value
        self.need_redraw(self.rect)
    pos = property(__get_pos, __set_pos)

    def __get_contents_rect(self):
        return self.rect
    contents_rect = property(__get_contents_rect)

    def __get_contents_size(self):
        return self.contents_rect.size
    contents_size = property(__get_contents_size)

    def __get_contents_pos(self):
        return self.contents_rect.pos
    contents_pos = property(__get_contents_pos)

    def __get_window(self):
        from window import Window
        if isinstance(self.parent, Window):
            return self.parent
        return self.parent.window
    window = property(__get_window)

    def __get_screen(self):
        return self.parent.screen
    screen = property(__get_screen)

    def set_rect(self, r):
        self.rect = r
        # TODO : emmit need resize ?

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

    def focus_child(self, w):
        """Set the focus on a given child"""
        self.focused = w

    def add(self, w):
        """Add a child to the widget"""
        self.children.append(w)
        self.emit('add-child', w)   # XXX: remove ?
        self.organized = False
        self.resized = False

    def destroy(self):
        if not self.parent: # Just to ensure we are not already destroyed
            return
        self.parent.remove(self)
        self.emit('destroyed')
        for c in self.children[:]:
            c.destroy()
        self.parent = None

    def remove(self, w):
        """Remove a child from the widget"""
        self.children.remove(w)
        self.organized = False
        self.resized = False
        self.surface = None
        self.need_redraw(self.rect)

    def need_redraw(self, rect):
        self.surface = None
        if self.parent is not None:
            self.parent.need_redraw(rect.move(self.pos))

    def draw(self, painter):
        """Draw the widget on a painter object

        The position where we paint is stored in the painter itself
        (opengl style)
        """
        if self.store_surface and self.surface is None:
            surface = painter.surface_from_size(self.size)
            self.store_surface = False
            self.draw(painter.to_surface(surface))
            self.store_surface = True
            self.surface = surface

        if self.surface:
            painter.draw_surface(self.surface)
            return

        painter.draw(self)

        for c in self.children:
            painter.move(c.pos)
            mask = painter.mask
            painter.clip(c.rect)
            if painter.mask.intersect(c.rect):
                c.draw(painter)
            painter.mask = mask
            painter.umove(c.pos)

    def do_organize(self):
        if not self.organized:
            self.organize()
            self.need_redraw(self.rect)
        for c in self.children:
            c.do_organize()
        self.organized = True

    def organize(self):
        """Set all children size and position"""
        # By default all the children are the same size than the
        # widget
        for c in self.children:
            c.pos = self.contents_pos
            c.size = self.contents_size

    def do_resize(self):
        for c in self.children:
            c.do_resize()
        if self.resized:
            return
        self.resize()
        self.resized = True

    def resize(self):
        if not self.fixed_min_size:
            self.min_size = Vect.merge(*[c.min_size for c in self.children])
        if not self.fixed_optimal_size:
            self.optimal_size = Vect.merge(
                self.min_size,
                *[c.optimal_size for c in self.children])

    def sorted_children(self):
        """Return the children, sorted with the one on top first"""
        # For the moment I suppose that none of the children overlap,
        # so we don't sort anything
        return self.children

    def mouse_down(self, pos):
        for c in self.sorted_children():
            cpos = pos - c.pos
            if not cpos in c.rect:
                continue
            if c.mouse_down(cpos):
                self.focused = c
                return True
        if self.clickable:
            self.emit('mouse-down', pos)
            return True
        return False

    def mouse_down_cancel(self):
        """Cancel the last mouse down event

        This function is mainly used for scrollable area, where we
        don't know from the beginning if we are clicking a widget, or
        just moving the area.
        """
        if self.focused:
            self.focused.mouse_down_cancel()
            self.focused = None

    def mouse_up(self, pos):
        if not self.focused:
            self.emit('mouse-up', pos)
            return True
        else:
            ret = self.focused.mouse_up(pos - self.focused.pos)
            self.focused = None
            return ret

    def mouse_motion(self, pos):
        if not self.focused:
            self.emit('mouse-motion', pos)
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
