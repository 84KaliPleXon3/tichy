# -*- coding: utf-8 -*-
#
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

from card import Card


class Box(list):

    def __init__(self, size):
        self.size = size

    def __repr__(self):
        ret = StringIO()
        self.write(ret)
        return ret.getvalue()

    def write(self, file):
        print >>file, "%i/%i" % (len(self), self.size)
        for c in self:
            print >>file, c.q

    def full(self):
        return len(self) >= self.size

    def append(self, c):
        assert not self.full()
        super(Box, self).append(c)

    @staticmethod
    def read(file, dic):
        l, s = [int(x) for x in file.readline().split("/")]
        ret = Box(s)
        for c in xrange(l):
            q = file.readline().strip()
            ret.append(dic[q])
        return ret
