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


class Vect(tuple):

    def __new__(cls, x, y):
        return tuple.__new__(cls, (x, y))

    def __init__(self, *args):
        pass

    def __get_x(self):
        return self[0]

    def __get_y(self):
        return self[1]

    x = property(__get_x)
    y = property(__get_y)

    def to_list(self):
        return self

    def __add__(self, v):
        return Vect(self[0] + v[0], self[1] + v[1])

    def __sub__(self, v):
        return Vect(self[0] - v[0], self[1] - v[1])

    def __mul__(self, k):
        return Vect(self[0] * k, self[1] * k)

    def __div__(self, k):
        return Vect(self[0] / k, self[1] / k)

    def __neg__(self):
        return Vect(-self[0], -self[1])

    def set(self, axis, value):
        assert isinstance(value, int), value
        return Vect(value, self[1]) if axis == 0 else Vect(self[0], value)

    @staticmethod
    def merge(*vs):
        x, y = 0, 0
        for v in vs:
            x, y = max(x, v.x), max(y, v.y)
        return Vect(x, y)


def asvect(o):
    if isinstance(o, Vect):
        return o
    return Vect(o[0], o[1])


class Rect(tuple):

    def __new__(cls, x, y):
        return tuple.__new__(cls, (Vect(*x), Vect(*y)))

    def __init__(self, *args):
        pass

    def to_list(self):
        return self[0][0], self[0][1], self[1][0], self[1][1]

    def __mul__(self, k):
        return Rect(self[0] * k, self[1] * k)

    pos = property(lambda self: self[0])
    size = property(lambda self: self[1])

    left = property(lambda self: self[0][0])
    right = property(lambda self: self[0][0] + self[1][0])
    top = property(lambda self: self[0][1])
    bottom = property(lambda self: self[0][1] + self[1][1])
    width = property(lambda self: self[1][0])
    height = property(lambda self: self[1][1])

    def moveto(self, pos):
        return Rect(asvect(pos), self[1])

    def move(self, pos):
        return Rect(self[0] + asvect(pos), self[1])

    def resize(self, size):
        return Rect(self[0], asvect(size))

    def __contains__(self, v):
        return v[0] >= self.left and v[1] >= self.top and \
                v[0] < self.right and v[1] < self.bottom

    def intersect(self, r):
        return r.left < self.right and r.right > self.left and \
               r.top < self.bottom and r.bottom > self.top

    def intersect_(self, r):
        return self.intersect(r)

    def is_empty(self):
        return self[1][0] == 0 and self[1][1] == 0

    def clip(self, r):
        r = asrect(r)
        left = max(self.left, r.left)
        right = min(self.right, r.right)
        top = max(self.top, r.top)
        bottom = min(self.bottom, r.bottom)
        right = max(right, left)
        bottom = max(bottom, top)
        return Rect((left, top), (right - left, bottom - top))

    def merge(self, r):
        r = asrect(r)
        left = min(self.left, r.left)
        right = max(self.right, r.right)
        top = min(self.top, r.top)
        bottom = max(self.bottom, r.bottom)
        return Rect((left, top), (right - left, bottom - top))

    def inside(self, r):
        """Return a rect of the same size put inside the rect r"""
        r = asrect(r)
        width = min(self.width, r.width)
        height = min(self.height, r.height)
        left = max(self.left, r.left)
        top = max(self.top, r.top)
        return Rect((left, top), (width, height))


def asrect(o):
    if isinstance(o, Rect):
        return o
    if len(o) == 2:
        return Rect(o[0], o[1])
    if len(o) == 4:
        return Rect(o[0:2], o[2:4])


if __name__ == '__main__':
    v = asvect((1, 2))
    print v
    v = asvect(v)
    print v
