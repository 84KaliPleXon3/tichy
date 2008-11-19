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

import pygame
import pygame.image
import pygame.font
import pygame.locals

from geo import Vect, Rect, asvect, asrect
from painter import Painter
from tichy.tasklet import Tasklet, Wait
from tichy.events_loop import MainLoop
from tichy.object import Object

from font import Font

import logging
logger = logging.getLogger('sdl_display')


class SdlPainter(Painter):
    """ Painter Engine that use SDL for rendering

    SDL can be used with X11, or direct frame buffer.  It only offers
    simple blitting functions, but do it very efficiently.
    """

    def __init__(self, size, fullscreen=False):
        Painter.__init__(self, Vect(0, 0), Rect((0, 0), size))
        pygame.init()
        flags = pygame.RESIZABLE
        self.surface = pygame.display.set_mode(size, flags)
        pygame.display.set_caption("Tichy")

    def to_surface(self, surface):
        """Return a engine similar to this one but
        drawing into a given surface"""
        ret = SdlPainter.__new__(SdlPainter)
        ret.pos = Vect(0, 0)
        ret.mask = Rect((0, 0), surface.get_size())
        ret.surface = surface
        return ret

    def set_mask(self, mask):
        super(SdlPainter, self).set_mask(mask)
        rr = self.mask.move(self.pos)
        self.surface.set_clip((rr.pos.x, rr.pos.y, rr.size.x, rr.size.y))

    def clip(self, r):
        super(SdlPainter, self).clip(r)
        self.surface.set_clip(self.mask.move(self.pos).to_list())

    def surface_from_size(self, size):
        # This is not really optimized, because we use transparent
        # surface all the time
        return pygame.Surface(size, pygame.SRCALPHA, 32).convert_alpha()

    def surface_from_svg(self, path):
        import rsvg
        import cairo
        import array
        # NOTE: currently pygame has a bug where it switches channel
        # in the buffer before drawing it. The fix below is
        # inefficient and is not being included for now. So the svg
        # colors will be off

        # commented out pygame channel switch bug
        #
        #import re
        # create pygame image surface
        # there is a bug in pygame where it switches buffer channels
        # r"\2\1\4\3"
        #fixed_buf = re.sub (r"(.)(.)(.)(.)", r"\4\3\2\1", buf.tostring())
        #surf = pygame.image.fromstring(fixed_buf, (width,height), "ARGB")

        svg = rsvg.Handle(file=path)
        width, height = svg.props.width, svg.props.width
        stride = width * 4
        # create a character data structure because pycairo does not
        # seem to handle python types
        buf = array.array('c', chr(0) * width * height * 4)
        cairo_surface = cairo.ImageSurface.create_for_data(
            buf, cairo.FORMAT_ARGB32, width, height, stride)
        cairo_context = cairo.Context(cairo_surface)
        svg.render_cairo(cairo_context)
        surf = pygame.image.frombuffer(buf.tostring(),
                                       (width, height), "ARGB")
        return surf.convert_alpha()

    def surface_from_image(self, path):
        if path[-3:] == 'svg':
            try:
                return self.surface_from_svg(path)
            except Exception, e:
                logger.error("can't use surface_from_svg : %s", e)
        surf = pygame.image.load(path)
        return surf.convert_alpha()

    def surface_from_text(self, font, text, color=None, length=None):
        assert isinstance(text, (str, unicode)), text
        return font.render(self, text, color=color, length=length)

    def font_from_file(self, file, size=24):
        return Font(file, size)

    def draw_surface(self, surf, area=None):
        if area:
            area = asrect(area)
            self.surface.blit(surf, self.pos.to_list(), area.to_list())
        else:
            self.surface.blit(surf, self.pos.to_list())

    def fill(self, color, size=None):
        if size:
            self.surface.fill(color,
                              (self.pos.x, self.pos.y, size[0], size[1]))
        else:
            self.surface.fill(color)

    def flip(self, rect=None):
        if not rect:
            pygame.display.flip()
        else:
            pygame.display.update(rect.to_list())

import gobject


class SdlEventsLoop(Object):
    """This is our events loop, that use SDL to get the inputs
    """

    def __init__(self):
        super(SdlEventsLoop, self).__init__()
        self.events = []
        self.running = True
        self.clock = pygame.time.Clock()

    def next(self):
        self.events = []
        if pygame.display.get_init():
            for event in pygame.event.get(pygame.locals.MOUSEMOTION):
                if event.buttons[0]:
                    self.events = [('mouse-motion', (asvect(event.pos), ))]

            for event in pygame.event.get():
                if event.type == pygame.locals.MOUSEBUTTONDOWN:
                    self.events.append(('mouse-down', (asvect(event.pos), )))
                elif event.type == pygame.locals.MOUSEBUTTONUP:
                    self.events.append(('mouse-up', (asvect(event.pos), )))
                elif event.type == pygame.locals.KEYDOWN:
                    self.events.append(('key-down', (event, )))
                elif event.type == pygame.locals.VIDEORESIZE:
                    self.events.append(('resized', (asvect(event.size), )))
                    self.surface = pygame.display.set_mode(event.size,
                                                           pygame.RESIZABLE)
        self.emit('tick')

    def run(self):
        # OK here we are in fact relying on the gobject main loop. Why
        # ? Because we want to be able to use DBus, and sofar we can
        # only use DBus with gobject main loop.
        self.gobject_loop = gobject.MainLoop()
        # This is used to synchronize the gobject loop and the sdl_loop

        def on_tick(*args):
            self.next()
            return True
        gobject.timeout_add(50, on_tick)
        self.gobject_loop.run()

    def quit(self):
        self.running = False
        self.gobject_loop.quit()

    def debug(self):
        import gc
        gc.collect()
        print len(gc.get_objects())

    def timeout_add(self, time, callback, *args):
        return gobject.timeout_add(time, callback, *args)

    def __get_dbus_loop(self):
        import dbus
        return dbus.mainloop.glib.DBusGMainLoop()

    dbus_loop = property(__get_dbus_loop)
