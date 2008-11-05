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


from widget import Widget
from geo import Vect

class Spring(Widget):
    """This widget does nothing but tries to extend, so it can be used to separate other widget"""
    def __init__(self, parent, axis, expand=True, **kargs):
        self.axis = axis
        super(Spring, self).__init__(parent, expand=True, **kargs)#optimal_size = Vect(0, 640), **kargs)
        
    def resistance(self, axis):
        return 0 if axis == self.axis else 1

