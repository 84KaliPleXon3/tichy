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
from geo import Rect, Vect

import gobject  # Only for the timeout

class Button(Widget):
    def __init__(self, parent, holdable = False, **kargs):
        super(Button, self).__init__(parent, **kargs)
        self.__pressed = False
        self.store_surface = True
        self.clickable = True
        self.holdable = holdable
        self.hold_connection = None
        
    def get_style_dict(self):
        ret = super(Button, self).get_style_dict()
        if self.__pressed and 'pressed-style' in ret:
            ret = ret['pressed-style'].apply(self) # TODO: this could be slow
        return ret
        
    def __get_pressed(self):
        return self.__pressed
    def __set_pressed(self, value):
        if value == self.__pressed:
            return
        self.surface = None
        self.__pressed = value
        self.need_redraw(self.rect)
    pressed = property(__get_pressed, __set_pressed)
    
    def mouse_down(self, pos):
        self.pressed = True
        super(Button, self).mouse_down(pos)
        
        if self.holdable:   # If the button can be hold, then we set up the callback
            def on_hold(*args):
                self.hold()
            self.hold_connection = gobject.timeout_add(self.holdable, on_hold)
        
        return True
        
    def mouse_down_cancel(self):
        self.pressed = False
        self.unhold()
        return super(Button, self).mouse_down_cancel()
        
    def mouse_up(self, pos):
        if self.pressed:
            self.click()
        self.pressed = False
        self.unhold()
        return super(Button, self).mouse_up(pos)
        
    def hold(self):
        if self.pressed:
            self.mouse_down_cancel()
        print "hold", self
        self.emit("holded")
        
    def unhold(self):
        """This has to be called every time we need to cancel the hold"""
        if self.hold_connection:
            gobject.source_remove(self.hold_connection)
            self.hold_connection = None
            
    def destroy(self):
        self.unhold()
        super(Button, self).destroy()
        
    def click(self):
        self.emit('clicked')
        
    def mouse_motion(self, pos):
        if (pos in Rect((0,0), self.size)) != self.pressed:
            self.pressed = pos in self.rect
        return super(Button, self).mouse_motion(pos)
        
