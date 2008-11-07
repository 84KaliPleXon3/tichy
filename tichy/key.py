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

# This is just a hack to import all the K_* values
#
# XXX: do it a better way

import pygame
from pygame import *

class SpecialKeys(object):
    pass
K_NEXT_LAYOUT = SpecialKeys()
    
def unicode(key, mod):
    """Return the unicode associated with a key and a modifier"""
    # XXX: This thing has to be removed from here
    # XXX: The unicode should depends of the keyboard 
    if K_a <= key <= K_z:
        ret = chr(ord('a') + key - K_a)
        if mod == 1:
            ret = ret.upper()
        return ret
    if key == K_SPACE:
        return ' '
    if key == K_PERIOD:
        return '.'
