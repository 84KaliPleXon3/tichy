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

from random import choice

from card import Card


class Dic(list):

    @staticmethod
    def read(file):
        ret = Dic()
        for line in file:
            line = line.strip()
            if not line or line[0] == '#':
                continue
            ret.append(Card.read(line))
        return ret

    def __getitem__(self, key):
        if isinstance(key, int):
            return super(Dic, self).__getitem__(key)
        for c in self:
            if c.q == key:
                return c
        raise KeyError("can't find card %s" % key)

    def get(self):
        ret = choice(self)
        self.remove(ret)
        return ret

    def append(self, card):
        for c in self:
            if c.q == card.q:
                raise "card %s already in the dict" % c.q
        super(Dic, self).append(card)

    def remove(self, value):
        if isinstance(value, Card):
            value = value.q
        if isinstance(value, unicode):
            for v in self:
                if v.q == value:
                    value = v
                    break
        super(Dic, self).remove(value)
