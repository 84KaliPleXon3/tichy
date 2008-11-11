#!/usr/bin/python -tt
#
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

import time

import tichy
from tichy import gui


class Clock(tichy.Gadget):

    name = 'Clock'

    def run(self, window):
        self.text = tichy.Text('')
        # XXX: we shouldn't have to guess the size here !
        self.text.view(window, optimal_size=gui.Vect(32 * 8, 64))
        tichy.mainloop.timeout_add(500, self.on_timeout)
        yield None

    def on_timeout(self):
        self.text.value = time.strftime("%H:%M", time.localtime())
        return True
