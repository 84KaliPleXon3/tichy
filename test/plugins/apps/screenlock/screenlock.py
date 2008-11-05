#    Tichy
#    copyright 2008 Michael "Goodwill" (openmoko /a/ webhippo.org)
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

import tichy
from tichy import gui
from tichy.gui import Vect, Rect

import pygame

import logging
logger = logging.getLogger('App.ScreenLock')

class ScreenLockWidget(gui.SurfWidget):

    ##########################################################################
    def __init__(self, parent, size):
        super(ScreenLockWidget, self).__init__(parent, size)

        self.attempt_pattern  = set([])

        # grid settings
        self.background_color = (0, 0, 0)
        self.grid_width = size[0]
        self.grid_height = size[1]
        self.cell_width  = 116
        self.cell_height = 133
        self.line_color = (88,88,88)

        # marker settings
        self.marker_args = ( (0,192,0), 25, 2 )
        self.selected_marker_args = ( (0,192,0), 25, 0 )

        srvc = tichy.Service('ScreenLock')
        self.unlock_pattern = srvc.pattern_data

        self.clear()

    ##########################################################################
    def clear(self):
        self.draw_grid()
        self.draw_unlock_pattern()
        self.need_redraw(self.rect)


    ##########################################################################
    def draw_grid(self):

        self.surface.fill(self.background_color)

        # draw grid
        start_x = 0
        x = y = 0

        # TODO: this return (0,0) in guip, uncomment next 3 lines
        # and comment out the work around to see
        #print self.size
        #end_x = self.size.x
        #end_y = self.size.y
        # work around
        end_x = self.size.x or self.grid_width
        end_y = self.size.y or self.grid_height

        # horizontal lines
        while y <= end_y:
            pygame.draw.line(self.surface, self.line_color,
                             (start_x, y),
                             (end_x, y), 2)
            y += self.cell_height


    ##########################################################################
    def draw_unlock_pattern(self):
        for cell in self.unlock_pattern:
            self.draw_marker(cell)

    ##########################################################################
    def draw_marker(self, cell, selected=False, redraw=False):
        args = list(selected and self.selected_marker_args or self.marker_args)
        marker_pos = \
         (
            (self.cell_width / 2) +  self.cell_width * (cell[1]- 1),
            (self.cell_height / 2) + self.cell_height * (cell[0] - 1)
         )
        args.insert(1, marker_pos)
        r = pygame.draw.circle(self.surface, *args)
        if redraw:
            redraw_rect = Rect((r.left, r.top), (r.width, r.height))
            self.need_redraw(redraw_rect)

    ##########################################################################
    def clickable(self):
        return True

    ##########################################################################
    def reset_attempt(self):
        self.attempt_pattern = set([])

    ##########################################################################
    def mouse_down(self, pos):
        self.reset_attempt()
        self.clear()
        self.mouse_pos = pos
        self.mouse_motion(pos)
        return True

    ##########################################################################
    def mouse_up(self, pos):
        if self.unlock_pattern == self.attempt_pattern:
            self.emit('unlocked-screen')
            return 

        self.reset_attempt()
        self.clear()

    ##########################################################################
    def mouse_motion(self,pos):
        cell = ( (pos[1] / self.cell_height) + 1,
                 (pos[0] / self.cell_width) + 1 )
        if cell in self.unlock_pattern and cell not in self.attempt_pattern:
            self.attempt_pattern.add(cell)
            self.draw_marker(cell, selected=True, redraw=True)


class ScreenLockApp(tichy.Application):
    """Screen Lock"""
    name = 'Lock'
    icon = 'icon.png'
    category = 'general' # So that we see the app in the launcher

    ##########################################################################
    def __init__(self, *args):
        super(ScreenLockApp, self).__init__(*args)

    ##########################################################################
    def run(self, parent):
        self.window = gui.Window(parent, modal = True)
        vbox = gui.Box(self.window, axis=1, border=0, spacing=0)
        self.lock_widget = ScreenLockWidget(vbox, Vect(480, 560))

        size = Vect(42,42)
        gui.Label(vbox, '       Trace the pattern to unlock',
                  min_size=size, optimal_size=size)

        yield tichy.Wait(self.lock_widget, 'unlocked-screen')
        self.window.destroy()



class ScreenLockService(tichy.Service):
    service = 'ScreenLock'

    ##########################################################################
    def __init__(self):
        super(ScreenLockService, self).__init__()
        # unlock patterns
        # format: ( (row, col), (row, col)
        # first rows and columns start at 1
        self._patterns = \
                {
                  'Zorro':
                    set([(1, 1), (4, 4), (1, 4), (2, 3), (3, 2), (4, 1) ]),
                  'Four Corners':
                    set([ (1, 1), (1, 4), (4, 1), (4, 4) ]),
                  'Top-most Marching Line':
                    set([ (1, 1), (1, 1), (1, 3), (1, 4) ]),
                  'Top Marching Line':
                    set([ (2, 1), (2, 2), (2, 3), (2, 4) ]),
                  'Bottom Marching Line':
                    set([ (3, 1), (3, 2), (3, 3), (3, 4) ]),
                  'Bottom-most Marching Line':
                    set([ (4, 1), (4, 2), (4 ,3), (4, 4) ])
                }
        # default and fallback pattern
        self._pattern = 'Zorro'

    ##########################################################################
    def get(self):
        return ScreenLockApp

    ##########################################################################
    def __get_patterns(self):
        return sorted(self._patterns.keys())

    def __set_pattern(self, x):
        if x in self._patterns:
            self._pattern = x
            return
        self._pattern = 'Zorro'

    ##########################################################################
    def __get_pattern(self):
        return self._pattern

    def __get_pattern_data(self):
        return self._patterns[self._pattern]

    ##########################################################################
    pattern = property(__get_pattern, __set_pattern)
    patterns = property(__get_patterns)
    pattern_data = property(__get_pattern_data)

    ##########################################################################
    def run(self, window):
        ScreenLockApp(window).start()

