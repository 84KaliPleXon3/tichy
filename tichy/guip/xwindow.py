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

import logging
logger = logging.getLogger('XWindow')

from widget import Widget
try:
    import Xlib
    import Xlib.display
    import Xlib.protocol.event
    import Xlib.ext.xtest
    import Xlib.XK
except ImportError, e:
    logger.error("can't import Xlib %s", e)
    Xlib = None

import pygame
import time

# XXX: we have a few busy wait in this class


class XWindow(Widget):
    """Experimental support for XWindow"""

    def __init__(self, parent, expand=True, **kargs):
        super(XWindow, self).__init__(parent, expand=expand, **kargs)
        self.x_window = None

    def __get_id(self):
        return self.x_window.id
    id = property(__get_id)

    def create_x_window(self):
        if self.x_window is not None:
            return
        if not Xlib:
            self.x_display = None
            return

        # First we get the xwindow id of the SDL window
        self.x_display = Xlib.display.Display()
        self.x_screen = self.x_display.screen()
        info = pygame.display.get_wm_info()
        x_window_id = info['window']
        x_window = self.x_display.create_resource_object('window',
                                                         x_window_id)
        pos = self.screen_pos()
        # Create a sub window
        self.x_window = x_window.create_window(
            pos.x, pos.y, self.size.x, self.size.y, 0,
            self.x_screen.root_depth,
            Xlib.X.CopyFromParent,
            Xlib.X.CopyFromParent,
            background_pixel=self.x_screen.white_pixel,
            colormap=Xlib.X.CopyFromParent,
            event_mask=Xlib.X.StructureNotifyMask)
        self.x_window.map()

        # Do a busy wait for X reply
        while True:
            event = self.x_display.next_event()
            if event.type == Xlib.X.MapNotify and \
                    event.window == self.x_window:
                break
        self.x_display.sync()

        # We get the Notify Events
        self.emit('exposed')

    def hide(self):
        if self.x_window:
            self.x_window.destroy()
            # Do a busy wait for X reply
            while 1:
                event = self.x_display.next_event()
                if event.type == Xlib.X.DestroyNotify and \
                        event.window == self.x_window:
                    break
        self.x_window = None

    def show(self):
        if not self.x_window:
            self.create_x_window()

    def organize(self):
        self.show()

    def destroy(self):
        self.hide()
        super(XWindow, self).destroy()

    def key_down(self, key):
        # If a key down event arrives, we send it to the x_window (in
        # fact here we just send it to X and assume that the x window
        # has the focus. I am not sure it is the best way...)
        if not key.key:
            return
        # We need to check the modifiers to simulate the proper key
        # press events
        if key.mod == 1:
            modifier = self.x_display.keysym_to_keycode(Xlib.XK.XK_Shift_L)
        else:
            modifier = None
        keycode = self.x_display.keysym_to_keycode(key.key)
        if modifier:
            Xlib.ext.xtest.fake_input(self.x_display, Xlib.X.KeyPress,
                                      modifier)
            self.x_display.sync()
        Xlib.ext.xtest.fake_input(self.x_display, Xlib.X.KeyPress, keycode)
        self.x_display.sync()
        Xlib.ext.xtest.fake_input(self.x_display, Xlib.X.KeyRelease, keycode)

        if modifier:
            self.x_display.sync()
            Xlib.ext.xtest.fake_input(self.x_display, Xlib.X.KeyRelease,
                                      modifier)
        return True

    def start_app(self, *cmd):
        # XXX: This only works if we run with NO windows manager I
        #      need to find a way to make it work even with a window
        #      manager, Or at least write a warning if there is a WM
        #      running.
        import subprocess

        self.x_screen.root.change_attributes(
            event_mask=Xlib.X.SubstructureNotifyMask)
        self.x_display.sync()

        process = subprocess.Popen(*cmd)

        while True:
            event = self.x_display.next_event()
            if event.type == Xlib.X.CreateNotify and \
                    event.parent == self.x_screen.root:
                event.window.reparent(self.x_window, 0, 0)
                event.window.map()
                self.x_display.sync()
                # TODO: We shouldn't give the focus to this XWindow We
                #       should send the vent in the key_down method
                self.x_display.set_input_focus(
                    event.window, Xlib.X.RevertToParent, Xlib.X.CurrentTime)
                break

        self.x_screen.root.change_attributes(event_mask=Xlib.X.NONE)

        return process
