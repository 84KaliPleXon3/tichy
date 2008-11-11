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


from box import Box
from geo import Vect


class Table(Box):

    def __init__(self, parent, axis=0, nb=3, **kargs):
        # Here we may need to set the optimal size or the size ?? (I
        # am not sure)
        self.nb = nb
        super(Table, self).__init__(parent, axis, **kargs)

    def cell_optimal_size(self):
        return Vect(max(w.optimal_size[0] for w in self.children),
                    max(w.optimal_size[1] for w in self.children))

    def cell_min_size(self):
        return Vect(max(w.min_size[0] for w in self.children),
                    max(w.min_size[1] for w in self.children))

    def resize(self):
        if not self.children:
            return
        axis = self.axis
        cell_optimal_size = self.cell_optimal_size()
        cell_min_size = self.cell_min_size()

        nb_per_line = self.nb

        # Quite ugly algorithm to compute the number of lines
        # I do like this cause I want to avoid importing math
        nb_lines = len(self.children) / nb_per_line
        if len(self.children) % nb_per_line != 0:
            nb_lines += 1

#         self.optimal_size = Vect(nb_per_line * cell_optimal_size[0],
#                                  nb_lines * cell_optimal_size[1])
        self.min_size = Vect(
            nb_per_line * (cell_min_size[0] + self.spacing) - self.spacing,
            nb_lines * (cell_min_size[1] + self.spacing) - self.spacing)

        self.optimal_size = self.min_size

    def organize(self):
        if not self.children:
            return
        axis = self.axis
        cell_size = self.cell_min_size()
        for i, c in enumerate(self.children):
            c.pos = Vect(0, 0).set(
                axis, i / self.nb * (cell_size[axis] + self.spacing)).set(
                axis - 1, i % self.nb * (cell_size[axis - 1] + self.spacing))
            c.size = cell_size
