#!/usr/bin/env python
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

"""Sound service"""

__docformat__ = 'reStructuredText'

import logging
logger = logging.getLogger('sound')

import subprocess
import re

import tichy

# XXX: This is VERY ugly ! Every time we try to get the master volume
#      it will start amixer from bash, and parse the result !!!  So it
#      is :
#
#          - slow
#
#          - blocking (all other things will have to wait until it is
#            done)
#
#          - ugly (using subprocess module here is a gross hack)
#
#      We should use a library (python-alsamixer for example) instead


class SoundService(tichy.Service):

    service = 'Sound'

    def __init__(self):
        super(SoundService, self).__init__()
        self.volume_re = re.compile(r'\[(\d+)%\]')

    def __get_volume(self):
        logger.info("Try to get volume")
        # XXX: worst piece of code I ever wrote !!!
        proc = subprocess.Popen(['amixer', 'get', 'PCM'],
                                stdout=subprocess.PIPE)
        ret = proc.communicate()[0]
        match = self.volume_re.search(ret)
        value = int(match.group(1))
        return value

    def __set_volume(self, value):
        # XXX: blocking
        logger.info("Try to set colume to %d", value)
        subprocess.call(['amixer', 'set', 'PCM', '%d%%' % value])

    volume = property(__get_volume, __set_volume)
