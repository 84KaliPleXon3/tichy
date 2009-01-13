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

import re


class Card(object):

    def __init__(self, q, a, comment=None):
        self.q = q
        self.a = a
        self.comment = comment

    def __repr__(self):
        return '%s -> %s' % (self.q, self.a)

    reg = re.compile(r"\s*(.*?)\s*"  \
                         r"->\s*(.*?)\s*"  \
                         r"(?:\[(.*)\])?\s*$")

    @staticmethod
    def read(line):
        ret = Card.reg.match(line)
        q, a, c = ret.group(1, 2, 3)
        return Card(q, a, c)
