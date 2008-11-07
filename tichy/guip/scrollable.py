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


from widget import Widget
from geo import Vect, Rect
from ..tasklet import Tasklet, WaitFirst, Wait

class Scrollable(Widget):
    """Special widget that can be scrolled in a given direction
    """
    def __init__(self, parent, axis = 1, **kargs):
        self.axis = axis
        super(Scrollable, self).__init__(parent, **kargs)
        self.click_pos = None
    
    def move_distance(self):
        return 32

    def mouse_down(self, pos):
        self.children[0].mouse_down(pos - self.children[0].pos)
        self.click_pos = (pos - self.children[0].pos)[self.axis]
        task = Tasklet(generator = self.motion_task(pos))
        task.start()
        return True
    
    def motion_task(self, pos):
        """This is the tasklet we use when we are in a motion"""
        child = self.children[0]
        click_pos = pos[self.axis] - child.pos[self.axis]
    
        # First we wait to move more than move_distance before we
        # actually move the child
        while True:
            e, args = yield WaitFirst(Wait(self, 'mouse-up'),
                                      Wait(self, 'mouse-motion'))
            pos = args[0]
            if e == 0:
                child.mouse_up(pos)
                return
            if e == 1:
                dist = click_pos + child.pos[self.axis] - pos[self.axis]
                if abs(dist) > self.move_distance():
                    break
        
        # OK now we are in motion mode
        child.mouse_down_cancel()
        # child.store_surface = True
        last_dist = None
        while True:
            e, args = yield WaitFirst(Wait(self, 'mouse-up'),
                                      Wait(self, 'mouse-motion'))
            pos = args[0]
            if e == 0:
                break
            if e == 1:
                # We use a step of 8
                dist = (pos[self.axis] - self.click_pos) / 8 * 8
                if dist == last_dist:
                    continue
                last_dist = dist
                child.pos = child.pos.set(self.axis, dist)
                # We ensure that we don't go too far
                if child.pos[self.axis] + child.size[self.axis] < self.size[self.axis]:
                    child.pos = child.pos.set(self.axis, self.size[self.axis] - child.size[self.axis])
                if child.pos[self.axis] > 0:
                    child.pos = child.pos.set(self.axis, 0)
                self.emit('scrolled')
            
        child.store_surface = False
        
    def resize(self):
        super(Scrollable, self).resize()
        # The minimum size allong the axis is always 0
        self.min_size = self.min_size.set(self.axis, 0)
        
    def organize(self):
        # We don't force the size on the scrollable axis
        child = self.children[0]
        child.size = child.optimal_size.set(self.axis - 1, self.size[self.axis - 1])
        
         # We ensure that we don't go too far
        if child.pos[self.axis] + child.size[self.axis] < self.size[self.axis]:
            child.pos = child.pos.set(self.axis, self.size[self.axis] - child.size[self.axis])
        if child.pos[self.axis] > 0:
            child.pos = child.pos.set(self.axis, 0)
        self.emit('scrolled')
            
class ScrollableSlide(Widget):
    def __init__(self, parent, **kargs):
        super(ScrollableSlide, self).__init__(parent, **kargs)
