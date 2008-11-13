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

"""The widget toolkit module.
"""

import logging
logger = logging.getLogger('gui')

backends = ['csdl', 'sdl']  # default backends
# This is a hack to be able to chose the gui backend before we load
# the module. If the variable `tichy_gui_backends` is set we use it as
# a list of backends to try.
import sys
if hasattr(sys.modules['__main__'], 'tichy_gui_backends'):
    backends = sys.modules['__main__'].tichy_gui_backends
# We can also specify etk backend using a command line option
# TODO: make this cleaner
if '--etk' in sys.argv:
    backends = ['etk']
elif '--gtk' in sys.argv:
    backends = ['gtk']
elif '--sdl' in sys.argv:
    backends = ['csdl', 'sdl']
elif '--csdl' in sys.argv:
    backends = ['csdl']


for backend in backends:
    try:
        if backend == 'csdl':
            from guic import *
        elif backend == 'sdl':
            from guip import *
        elif backend == 'gtk':
            from guig import *
        elif backend == 'etk':
            from guie import *
    except Exception:
        logger.warning("can't use backend %s", backend)
        if backend == backends[-1]:
            raise
    else:
        break
