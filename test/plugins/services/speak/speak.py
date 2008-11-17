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

"""Speaking service"""

from subprocess import Popen, PIPE

import logging
logger = logging.getLogger('speak')

import tichy


class Speak(tichy.Service):
    """Voice speaking service

    This service defines a single method : `speak`, that can read
    aloude a string.
    """
    service = 'Speak'

    def speak(self, text, lang='en', speed=120, voice='m1'):
        """invoke espeak to pronounce the text"""
        # We need to send str to the process
        if isinstance(text, unicode):
            text = text.encode('utf-8')
        try:
            logger.info("calling espeak")
            espeak = 'espeak -s%d -v%s+%s --stdout' % (speed, lang, voice)
            cmd = '%s | aplay' % espeak
            proc = Popen(cmd, stdin=PIPE, shell=True)
            proc.stdin.write(text)
            proc.stdin.close()
        except Exception, e:
            logger.error("can't use espeak : %s" % e)
            raise
