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


from geo import Vect, Rect, asvect, asrect
from widget import Widget
from label import Label
from button import Button


class Painter(object):
    """This class is used to draw all the widgets

    The idea is to subclass it when we want special drawing style.

    """

    def __init__(self, pos=None, mask=None):
        self.pos = pos or Vect(0, 0)
        self.mask = mask

    def draw_widget(self, w):
        style = w.get_style_dict()
        background = style.get('background')
        if background:
            background.draw(self, w.size)
        if isinstance(w, Label):
            self.draw_label(w)

    def draw_label(self, w):
        surf = self.surface_from_text(w.font, w.text, length=w.size.x)
        self.move(Vect(8, 8))
        self.draw_surface(surf)
        self.umove(Vect(8, 8))

    def draw(self, o):
        if isinstance(o, Widget):
            return self.draw_widget(o)

    def set_mask(self, rect):
        self.mask = Rect(rect[0], rect[1])

    def move(self, v):
        self.pos = self.pos + v
        self.mask = self.mask.move(-v)

    def umove(self, v):
        self.move(-v)

    def clip(self, r):
        self.mask = self.mask.clip(r)

    def to_surface(self, surface):
        """Return a engine similar to this one but drawing into a given
        surface
        """
        raise NotImplementedError

    def surface_from_size(self, size):
        """Create a new surface"""
        raise NotImplementedError

    def surface_from_image(self, path):
        """Create a new surface"""
        raise NotImplementedError

    def surface_from_text(self, font, text):
        """Create a new surface from a text"""
        raise NotImplementedError

    def font_from_file(self, file, size=24):
        raise NotImplementedError

    def draw_surface(self, surf, area=None):
        raise NotImplementedError

    def fill(self, color, size=None):
        raise NotImplementedError

    def draw_frame(self, frame, size):
        """Draw a frame. This function is in fact currently very slow !"""
        size = asvect(size)

        def indexes():
            width, height = size
            # The corners
            yield (0, 0), (0, 0)
            yield (width - 8, 0), (24, 0)
            yield (0, height - 8), (0, 24)
            yield (width - 8, height - 8), (24, 24)

            mwidth = width / 2
            mheight = height / 2

            # The borders
            for i in range(1, mwidth / 8):
                yield (i * 8, 0), (8, 0)
                yield (i * 8, height - 8), (8, 24)
            for i in range(mwidth / 8, width / 8 - 1):
                yield (i * 8, 0), (16, 0)
                yield (i * 8, height - 8), (16, 24)

            for i in range(1, mheight / 8):
                yield (0, i * 8), (0, 8)
                yield (width - 8, i * 8), (24, 8)
            for i in range(mheight / 8, height / 8 - 1):
                yield (0, i * 8), (0, 16)
                yield (width - 8, i * 8), (24, 16)
        frame.image.load(self)
        surf = frame.image.surf
        for dest, src in indexes():
            self.move(Vect(*dest))
            self.draw_surface(surf, Rect(asvect(src), Vect(8, 8)))
            self.umove(Vect(*dest))

        c1 = surf.get_at((16, 15))
        half_size = Vect(size[0] - 16, size[1] / 2 - 8)
        self.move(Vect(8, 8))
        self.fill(c1, half_size)
        self.umove(Vect(8, 8))

        c2 = surf.get_at((16, 16))
        self.move(Vect(8, half_size[1] + 8))
        self.fill(c2, half_size)
        self.umove(Vect(8, half_size[1] + 8))

    def flip(self, rect=None):
        raise NotImplementedError
