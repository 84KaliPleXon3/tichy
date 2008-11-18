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

import subprocess
import os
import signal

import tichy
import tichy.gui as gui
import tichy.item as item
from tichy.tasklet import Wait
from tichy.application import Application

from tichy.service import Service

import logging
logger = logging.getLogger('App.Terminal')


class Terminal(Application):

    name = "Terminal"
    category = 'main'
    experimental = True

    def run(self, window):
        self.window = gui.Window(window, modal=True)
        frame = self.view(self.window, back_button=True)

        vbox = gui.Box(frame, axis=1)
        self.x_window = gui.XWindow(vbox)

        keyboard = Service('Keyboard').get()
        keyboard.view(vbox)

        # We need to be sure that the xwindow is exposed before we can
        # start the subprocess...
        yield Wait(self.x_window, 'exposed')
        self.xterm = self.x_window.start_app('xterm')

        yield Wait(frame, 'back')
        self.window.destroy()
        os.kill(self.xterm.pid, signal.SIGKILL)
