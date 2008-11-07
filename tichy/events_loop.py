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


# TODO: remove this file

from tasklet import Tasklet, Wait
import gobject

        
class MainLoop():
    def __init__(self, window):
        super(MainLoop, self).__init__(self, window, (0,0))
        
    def get_events(self):
        return []
    def set_events(self, value):
        pass
        
    events = property(get_events, set_events)

            
    def wait_source(self):
        return MainLoop.Tick()
        
