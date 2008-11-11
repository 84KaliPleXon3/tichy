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

import os

from types import GeneratorType
from tasklet import Tasklet


class Object(object):
    """This class implements the observer patern

        I could use gobject.GObject instead.  But i think gobject may
        be overkill there... still thinking about it...
    """

    def __new__(cls, *args, **kargs):
        ret = object.__new__(cls)
        ret.__listeners = {}
        return ret

    def __init__(self, *kargs): # TODO: see why I hava to use __init__
                                # even with the __new__
        if not hasattr(self, '_Object__listeners'):
            self.__listeners = {}

    @classmethod
    def path(cls, path=None):
        # XXX: this path method sucks
        module_str = cls.__module__
        module = __import__(module_str)
        ret = os.path.dirname(module.__file__)
        if path:
            ret = os.path.join(ret, path)
        if os.path.exists(ret):
            return ret
        # If we didn't find the file then we check in the system dir
        for base in ['/usr/tichy', '/usr/share/tichy']:
            ret = os.path.join(base, path)
            if os.path.exists(ret):
                return ret

    @classmethod
    def open(cls, path):
        return open(self.path(path))

    def connect(self, event, callback, *args):
        """Connect the object to a given event"""
        return self.connect_object(event, callback, self, *args)

    def connect_object(self, event, callback, obj, *args):
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

    def emit(self, event, *args):
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


if __name__ == '__main__':

    def func(o, x):
        print x

    o = Object()
    o.connect('test', func)

    o.emit('test', 10)
