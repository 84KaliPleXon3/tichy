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

import os
import time

import tichy
from tichy import gui

import logging
logger = logging.getLogger('gadg.battery')


class Battery(tichy.Gadget):
    """Gadget that shows the battery usage"""

    name = 'Battery'

    def run(self, window):
        self.image = tichy.Image(self.path('battery0.png'), (32, 32))
        self.image.view(window)
        self.capacity = None
        # XXX: specific to openmoko !
        self.sys_dir = \
            '/sys/devices/platform/bq27000-battery.0/power_supply/bat/'
        tichy.mainloop.timeout_add(5000, self.on_timer)
        yield None

    def on_timer(self):
        # We get the battery status
        logger.debug("Update battery status")
        try:
            status_file = open(os.path.join(self.sys_dir, 'status'))
            status = status_file.read().strip()
            if status == 'Charging':
                self.image.path = self.path('charging.png')
                return True

            capacity_file = open(os.path.join(self.sys_dir, 'capacity'))
            capacity = int(capacity_file.read())
            if capacity == self.capacity:
                return 0
            # Let suppose the capacity goes from 0 to 100 (???)
            index = capacity * 4 / 100
            assert index > 0 and index <= 4, index
            self.image.path = self.path('battery%d.png' % index)
        except IOError:
            pass
        return True
