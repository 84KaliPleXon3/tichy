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


from widget import Widget
from tichy.object import Object
from geo import Rect, Vect


class Label(Widget):

    def __init__(self, parent, text ='',
                 font=None, font_size=None, **kargs):
        super(Label, self).__init__(parent, **kargs)
        # assert self.min_size.x == 0, self.min_size
        self.text = unicode(text)
        self.store_surface = True
        self.__font = font
        self.font_size = font_size

    def resize(self):
        return

    def __get_font(self):
        ret = self.__font or self.style_dict['font']
        if self.font_size:
            # TODO: does that takes time / memory ??
            ret = ret.resize(self.font_size)
        return ret
    font = property(__get_font)

    def __get_text(self):
        return self.__text

    def __set_text(self, value):
        # assert isinstance(value, (str, unicode))
        self.__text = unicode(value)
        # XXX: We need to recompute the optimal size !!!
        self.surface = None # TODO: remove that
        if not self.fixed_optimal_size:
            self.optimal_size = Vect(32 * len(value), 40)
        if not self.fixed_min_size:
            self.min_size = Vect(0, 40)
        self.need_redraw(self.rect)

    text = property(__get_text, __set_text)


if __name__ == '__main__':

    def test1():
        from image import Image
        from painter import Painter
        from geo import Vect, Rect
        from style import Style, Frame
        from sdl_painter import SdlPainter

        im = Image('frame.png')
        f = Frame(im)
        style = Style()
        style.background = f

        p = Painter(SdlPainter())

        l = Label(None, 'hello', style=style)
        l.rect = Rect((0, 0), (1, 1))
        l.draw(p)

        p.flip()

        raw_input()

    test1()
