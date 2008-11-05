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

from types import GeneratorType
from tichy.tasklet import Tasklet

cdef class Object:
    """This class implements the observer patern
    
        I could use gobject.GObject instead.
        But i think gobject may be overkill there... still thinking about it...
    """
    def __init__(self):
        self.__listeners = {}
        
    def connect(self, char* event, callback, *args):
        """Connect the object to a given event""" 
        return self.connect_object(event, callback, self, *args)
        
    def connect_object(self, char* event, callback, obj, *args):
        """Connect an event using a given object instead of self"""
        connection = (callback, obj, args)
        self.__listeners.setdefault(event, []).append(connection)
        return id(connection)
        
    def disconnect(self, oid):
        """remove a connection from the listeners"""
        for l in self.__listeners.itervalues():
            for c in l:
                if id(c) == oid:
                    l.remove(c)
                    return
        raise Exception("trying to disconnect a bad id")
        
    def emit(self, char* event, *args):
        """Emit a signal
        
           All the listeners will be notified
        """
        for e in self.__listeners.get(event, []):
            eargs = args + e[2]
            call = e[0](e[1], *eargs)
            # Now in case the callback is a generator, we turn it into a task
            # This allow us to directly connect to generators
            if type(call) is GeneratorType:
                Tasklet(generator=call).start()
        
    cdef void _emit(self, char* event) except *:
        """An optimized version of emit only for internal use"""
        for e in self.__listeners.get(event, []):
            e[0](e[1], *e[2])
            
    cdef void _emit_1(self, char* event, a) except *:
        """An optimized version of emit only for internal use"""
        for e in self.__listeners.get(event, []):
            e[0](e[1], a, *e[2])
