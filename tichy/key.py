
"""

"""

# This is just a hack to import all the K_* values
# XXX: do it a better way
import pygame
from pygame import *

class SpecialKeys(object):
    pass
K_SWITCH_LAYOUT = SpecialKeys()
    
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
