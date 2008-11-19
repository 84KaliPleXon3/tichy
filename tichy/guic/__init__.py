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

# Check that the compiled version is correct
from .version import __version__
if __version__ < 2:
    raise Exception("You need to recompile guic")

from .geo import Vect, Rect
from .image import ImageWidget
from .button import Button
from .label import Label
from .edit import Edit
from .screen import Screen
from .window import Window
from .box import Box, Fixed
from .table import Table
from .scrollable import Scrollable, ScrollableSlide
from .spring import Spring
from .widget import Widget
from .frame import Frame
from .sdl_painter import SdlPainter as Painter
from .sdl_painter import SdlEventsLoop as EventsLoop
from .surf_widget import SurfWidget
from .xwindow import XWindow
