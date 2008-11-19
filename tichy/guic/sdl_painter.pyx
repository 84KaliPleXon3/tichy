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


cdef extern from "pygame/pygame.h":
    ctypedef struct SDL_Surface
    cdef struct SDL_Rect:
        int x
        int y
        int w
        int h
    SDL_Surface* PySurface_AsSurface(object)
    int SDL_FillRect(SDL_Surface* dst, SDL_Rect* dstrect, int color)
    int SDL_BlitSurface(SDL_Surface *src, SDL_Rect *srcrect, SDL_Surface *dst, SDL_Rect *dstrect)
    SDL_Surface* SDL_DisplayFormat(SDL_Surface*)
    int SDL_SetAlpha(SDL_Surface *surface, int flag, int alpha)

cimport geo
from geo cimport Vect, Rect, c_Rect, c_Vect, c_rect_clip

from geo import asvect, asrect

cimport painter
from painter cimport Painter

cimport cobject
from cobject cimport Object

cimport widget
from widget cimport Widget

from button import Button

import label
from label import Label

import pygame
import pygame.image
import pygame.font
import pygame.locals

from font import Font

import logging
logger = logging.getLogger('sdl_display')

cdef class SdlPainter(Painter):
    def __init__(self, size, fullscreen = False):
        Painter.__init__(self, Vect(0,0), Rect((0,0), size))
        pygame.display.init()
        pygame.font.init()
        
        flags = pygame.FULLSCREEN if fullscreen else 0
        flags |= pygame.RESIZABLE
        self.surface = pygame.display.set_mode(size,flags)
        pygame.display.set_caption("Tichy")
        
    cdef void c_clip(self, c_Rect *r):
        c_rect_clip(&self.c_mask, r, &self.c_mask)
        self.surface.set_clip((self.c_mask.pos.x + self.c_pos.x, self.c_mask.pos.y + self.c_pos.y, self.c_mask.size.x, self.c_mask.size.y))
        
    cdef void c_set_mask(self, c_Rect *r):
        self.c_mask = r[0]
        self.surface.set_clip((r.pos.x + self.c_pos.x, r.pos.y + self.c_pos.y, r.size.x, r.size.y))
        
    cdef void _draw_widget(self, Widget w):
        cdef dict style = w.get_style_dict()
        background = style.get('background')
        if background:
            background.draw(self, w.size)
        if isinstance(w, Label):
            self._draw_label(w)
            
    cdef void _draw(self, o):
        self._draw_widget(o)
            
    cdef void _draw_label(self, Widget w):
        cdef c_Vect border
        border.x = 8; border.y = 8
        
        surf = self.surface_from_text(w.font, w.text, None, w.size.x)
        self.c_move(&border)
        self._draw_surface(surf, None)
        self.c_move(&border)
        
    cdef c_surface_from_size(self, c_Vect *size):
        # This is not really optimized, because we use transparent surface all the time
        return pygame.Surface((size.x, size.y), pygame.SRCALPHA, 32).convert_alpha(self.surface)


    def surface_from_svg(self,path):
        import rsvg
        import cairo
        import array
        # NOTE: currently pygame has a bug where it switches channel
        # in the buffer before drawing it. The fix below is inefficient
        # and is not being included for now. So the svg colors will be off

        # commented out fix pygame channel switch bug
        #import re
        # create pygame image surface
        # there is a bug in pygame where it switches buffer channels
        # r"\2\1\4\3"
        #fixed_buf = re.sub (r"(.)(.)(.)(.)", r"\4\3\2\1", buf.tostring())
        #surf = pygame.image.fromstring(fixed_buf, (width,height), "ARGB")

        svg = rsvg.Handle (file=path)
        width, height = svg.props.width, svg.props.width
        stride = width * 4
        # create a character data structure because pycairo does not
        # seem to handle python types   
        buf = array.array('c', chr(0) * width * height * 4)
        cairo_surface = cairo.ImageSurface\
            .create_for_data (buf, cairo.FORMAT_ARGB32,
                              width, height, stride)
        cairo_context = cairo.Context(cairo_surface)
        svg.render_cairo (cairo_context)
        surf = pygame.image.frombuffer(buf.tostring(),
                                       (width,height), "ARGB")
        return surf.convert_alpha()
        
    def surface_from_image(self, char* path):
        if path[-3:] == 'svg':
            try:
                return self.surface_from_svg(path)
            except Exception, e:
                logger.error("can't use surface_from_svg : %s", e)
            
        surf = pygame.image.load(path)
        return surf.convert_alpha(self.surface)
        
    def surface_from_text(self, font, text, color, length):
        return font.render(self, text, color = color, length = length)
        
    def font_from_file(self, file, size = 24):
        return Font(file, size)
        
    cdef void _draw_surface(self, surf, area):  # TODO: make it fast !!
        if area:
            self.surface.blit(surf, (self.pos.x, self.pos.y), area.to_list())
        else:
            self.surface.blit(surf, (self.pos.x, self.pos.y))
            
    cdef Painter _to_surface(self, surf):
        cdef SdlPainter ret = SdlPainter.__new__(SdlPainter)
        ret.surface = surf
        ret.c_pos.x = ret.c_pos.y = 0 # TODO: automatic initialisation ?
        rect = surf.get_rect()
        ret.c_mask.pos.x = ret.c_mask.pos.y = 0
        ret.c_mask.size.x = 480; ret.c_mask.size.y = 640
        return ret
            
    cdef void _fill(self, color, Vect size):
        self.surface.fill(color, (self.pos.x, self.pos.y, size.x, size.y))

    cdef void _flip(self, Rect rect):
        if rect is None:
            pygame.display.flip()
        else:
            pygame.display.update(rect.to_list())

    cdef void _draw_frame(self, frame, Vect size):
        """This is the super optimized version of draw_frame
        
            It doesn't work in some case (the edit widget) I don't know why
        """
        cdef int width = size.x
        cdef int height = size.y
        cdef int x = self.pos.x
        cdef int y = self.pos.y

        frame.image.load(self)
        surf = frame.image.surf
        
        cdef int c1 = self.surface.map_rgb(surf.get_at((16, 15)))
        cdef int c2 = self.surface.map_rgb(surf.get_at((16, 16)))
        
        cdef SDL_Surface* c_self_surf = PySurface_AsSurface(self.surface)
        cdef SDL_Surface* c_surf = PySurface_AsSurface(surf)
        
        # I don't know why I have to do this !!!
        SDL_SetAlpha(c_surf, 0, 255)
        
        # Draw the inside part
        cdef SDL_Rect rect
        rect.x = x + 8; rect.y = y + 8; rect.w = width - 16; rect.h = height / 2 - 8
        SDL_FillRect(c_self_surf, &rect, c1)
        rect.x = x + 8; rect.y = y + 8 + height / 2 - 8; rect.w = width - 16; rect.h = height / 2 - 8
        SDL_FillRect(c_self_surf, &rect, c2)
        
        # Draw the corners
        cdef SDL_Rect src_rect
        src_rect.x = src_rect.y = 0
        src_rect.w = src_rect.h = 8
        
        rect.x = x; rect.y = y; rect.w = rect.h = 8
        SDL_BlitSurface(c_surf, &src_rect, c_self_surf, &rect)
        rect.x = x + width - 8; rect.y = y; rect.w = rect.h = 8
        src_rect.x = 24
        SDL_BlitSurface(c_surf, &src_rect, c_self_surf, &rect)
        rect.x = x + width - 8; rect.y = y + height - 8; rect.w = rect.h = 8
        src_rect.y += 24
        SDL_BlitSurface(c_surf, &src_rect, c_self_surf, &rect)
        rect.x = x; rect.y = y + height - 8; rect.w = rect.h = 8
        src_rect.x -= 24
        SDL_BlitSurface(c_surf, &src_rect, c_self_surf, &rect)
        
        # Draw the borders
        # up border
        src_rect.x = 8; src_rect.y = 0
        for i from 1 <= i < width / 16:
            rect.x = x + i * 8; rect.y = y; rect.w = rect.h = 8
            SDL_BlitSurface(c_surf, &src_rect, c_self_surf, &rect)
        src_rect.x = 16
        for i from width / 16 <= i < width / 8 - 1:
            rect.x = x + i * 8; rect.y = y; rect.w = rect.h = 8
            SDL_BlitSurface(c_surf, &src_rect, c_self_surf, &rect)
        # down border
        src_rect.x = 8; src_rect.y = 24
        for i from 1 <= i < width / 16:
            rect.x = x + i * 8; rect.y = y + height - 8; rect.w = rect.h = 8
            SDL_BlitSurface(c_surf, &src_rect, c_self_surf, &rect)
        src_rect.x = 16
        for i from width / 16 <= i < width / 8 - 1:
            rect.x = x + i * 8; rect.y = y + height - 8; rect.w = rect.h = 8
            SDL_BlitSurface(c_surf, &src_rect, c_self_surf, &rect)
        # left border
        src_rect.x = 0; src_rect.y = 8
        for i from 1 <= i < height / 16:
            rect.x = x; rect.y = y + i * 8; rect.w = rect.h = 8
            SDL_BlitSurface(c_surf, &src_rect, c_self_surf, &rect)
        src_rect.y = 16
        for i from height / 16 <= i < height / 8 - 1:
            rect.x = x; rect.y = y + i * 8; rect.w = rect.h = 8
            SDL_BlitSurface(c_surf, &src_rect, c_self_surf, &rect)
        # right border
        src_rect.x = 24; src_rect.y = 8
        for i from 1 <= i < height / 16:
            rect.x = x + width - 8; rect.y = y + i * 8; rect.w = rect.h = 8
            SDL_BlitSurface(c_surf, &src_rect, c_self_surf, &rect)
        src_rect.y = 16
        for i from height / 16 <= i < height / 8 - 1:
            rect.x = x + width - 8; rect.y = y + i * 8; rect.w = rect.h = 8
            SDL_BlitSurface(c_surf, &src_rect, c_self_surf, &rect)
            
            
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
                    self.events = [ ('mouse-motion', (asvect(event.pos),) ) ]

            for event in pygame.event.get():
                if event.type == pygame.locals.MOUSEBUTTONDOWN:
                    self.events.append( ('mouse-down', (asvect(event.pos),) ) )
                elif event.type == pygame.locals.MOUSEBUTTONUP:
                    self.events.append( ('mouse-up', (asvect(event.pos),) ) )
                elif event.type == pygame.locals.KEYDOWN:
                    self.events.append( ('key-down', (event,) ) )
                elif event.type == pygame.locals.VIDEORESIZE:
                    self.events.append( ('resized', (asvect(event.size),) ) )
                    self.surface = pygame.display.set_mode(event.size,pygame.RESIZABLE)
        self.emit('tick')
        
    def run(self):
        # OK here we are in fact relying on the gobject main loop
        # Why ? Because we want to be able to use DBus, and sofar we can only use DBus with gobject main loop
        self.gobject_loop = gobject.MainLoop()
        # This is used to synchronize the gobject loop and the sdl_loop
        
        # XXX: we should make this mich faster,
        # because it is constantly called !
        # (It should be a C call, (and the 'next' call too) 
        gobject.timeout_add(50, self.on_tick)
        self.gobject_loop.run()
        
    def on_tick(self, *args):
        self.next()
        return True  
        
            
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


        
