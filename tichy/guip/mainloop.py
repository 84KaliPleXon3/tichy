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

import gobject
import pygame
import pygame.locals

import tichy.object
from geo import Vect, Rect, asvect, asrect


class EventsLoop(tichy.object.Object):
    """This is our events loop, that use SDL to get the inputs
    """

    def __init__(self):
        super(EventsLoop, self).__init__()
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

    def source_remove(self, connection):
        gobject.source_remove(connection)

    def __get_dbus_loop(self):
        import dbus.mainloop.glib
        return dbus.mainloop.glib.DBusGMainLoop()

    dbus_loop = property(__get_dbus_loop)

    def post_key_event(self, type, key, mod, str):
        """Simulate a key event from the user"""
        if type == 'down':
            type = pygame.KEYDOWN
        elif type == 'up':
            type = pygame.KEYUP
        pygame.event.post(pygame.event.Event(type, key=key, mod=mod,
                                             unicode=str))
