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
from geo import Vect, Rect
from window import Window


class Screen(Window):
    """Main widget for everything

    Screen is the widget that is at the end of the chain when we emit
    "need-redraw".  It is the only widget that start a redrawing
    sequence.  It may seem not optimized to always redraw from the top
    widget, but the idea is that you can then have transparency in any
    widgets.
    """

    def __init__(self, events_source, painter, **kargs):
        self.redraw_rect = None
        super(Screen, self).__init__(None, events_source=events_source,
                                     modal=False, **kargs)
        self.size = Vect(480, 640) # TODO find a better way
        self.painter = painter
        self.redraw_rect = self.rect
        self.monitor(events_source, 'tick', self.on_tick)

    screen = property(lambda self: self)

    def draw(self):
        if not self.redraw_rect:
            return
        assert self.painter.pos.x == self.painter.pos.y == 0
        # TODO: use virtual attribute
        self.painter.set_mask(self.redraw_rect)
        self.painter.fill((0, 0, 0), self.size) # The background color
        super(Screen, self).draw(self.painter)
        self.painter.flip(self.redraw_rect)
        self.redraw_rect = None

    def need_redraw(self, rect):
        self.redraw_rect = rect if not self.redraw_rect else \
            self.redraw_rect.merge(rect)

    def on_tick(self, event_source):
        self.tick()

    def tick(self):
        self.draw()
        super(Screen, self).tick()


if __name__ == '__main__':
    from box import VBox, HBox
    from label import Label
    from button import Button
    from geo import Vect, Rect
    from image import Image
    from scrollable import Scrollable
    from style import Style, Frame, AttributeFilter
    from sdl_painter import SdlPainterEngine, SdlTasklet
    from painter import Painter

    print "Hello"

    import gobject
    main_loop = gobject.MainLoop()

    im = Image('frame.png')
    f = Frame(im)

    im2 = Image('frame2.png')
    f2 = Frame(im2)

    style = Style(None)
    style.background = f

    button_style = Style(None)
    button_style.background = f2
    style.add_part(AttributeFilter('pressed', True), button_style)

    painter = Painter(SdlPainterEngine())
    screen = Screen(painter, style=style)

    vbox = VBox(screen)
    title = Label(vbox, "hello")
    # title.request_size((5,1) * 32)
    button = Button(vbox)

    def on_click(widget):
        print "click"
        main_loop.quit()
    button.connect('clicked', on_click)

    widget = Widget(vbox)
    widget.request_size((480, 128))
    scroll = Scrollable(widget)

    vbox2 = VBox(scroll)

    for i in range(10):
        b = Button(vbox2)
        # Label(b, str(i))

    tasklet = SdlTasklet(screen)
    tasklet.start()
    print 'tasklet started'
    main_loop.run()
