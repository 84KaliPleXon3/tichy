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

import tichy
from tichy import gui
from tichy.gui import Vect, Rect

import pygame
import Numeric

import logging
logger = logging.getLogger('App.Drawing')


class DrawingWidget(gui.SurfWidget):

    def __init__(self, parent, size):
        super(DrawingWidget, self).__init__(parent, size)
        self.__color = (255, 0, 0)
        self.__radius = 8
        self.shape = None
        self.update_shape()
        self.clear()

    def __get_radius(self):
        return self.__radius

    def __set_radius(self, value):
        self.__radius = value
        self.update_shape()

    radius = property(__get_radius, __set_radius)

    def __get_color(self):
        return self.__color

    def __set_color(self, value):
        self.__color = value
        self.update_shape()

    color = property(__get_color, __set_color)

    def clear(self):
        self.surface.fill((255, 255, 255))
        self.need_redraw(self.rect)

    def update_shape(self):
        radius = self.radius
        self.shape = pygame.Surface((radius * 2, radius * 2),
                                    pygame.SRCALPHA, 32).convert_alpha()
        self.shape.fill(self.color)
        alpha = pygame.surfarray.pixels_alpha(self.shape)
        x, y = Numeric.indices((radius * 2, radius * 2))
        dist = Numeric.sqrt((x - radius)**2 + (y - radius)**2)
        a = radius + 0.5 - dist
        a = Numeric.clip(a, 0, radius) * 255 / radius
        alpha[:] = a.astype(alpha.typecode())
        # alpha[:,:] = 255
        del alpha

    def clickable(self):
        return True

    def mouse_down(self, pos):
        self.mouse_pos = pos
        self.mouse_motion(pos)
        return True

    def mouse_motion(self, pos):
        # We need to draw several rects...
        dist = pos - self.mouse_pos
        norm = abs(dist.x) + abs(dist.y)
        nb_points = norm / self.radius + 1

        redraw_rect = Rect(pos, (0, 0))

        color = self.surface.map_rgb(self.color)
        for i in range(nb_points):
            ipos = (self.mouse_pos * i + pos * (nb_points - i)) / nb_points
            # rect = (ipos.x, ipos.y, self.pen_size, self.pen_size)
            self.surface.blit(self.shape, (ipos.x, ipos.y))
            # self.surface.fill(color, rect)
            # TODO: allow better rect constructors
            redraw_rect = redraw_rect.merge(Rect(
                    (ipos.x, ipos.y),
                    (self.radius * 2, self.radius * 2)))
        self.need_redraw(redraw_rect)
        self.mouse_pos = pos


class DrawingApp(tichy.Application):
    """A small application to test the keyboard widget"""

    name = 'Drawing'
    icon = 'icon.png'
    category = 'main'

    def __init__(self, *args):
        super(DrawingApp, self).__init__(*args)

    def run(self, window):
        frame = self.view(window, back_button=True)

        vbox = gui.Box(frame, axis=1)

        actor = frame.actor
        edit_item = actor.new_action('Edit')
        load_item = edit_item.new_action('Load')
        load_item.connect('activated', self.on_load)
        save_item = edit_item.new_action('Save')
        save_item.connect('activated', self.on_save)
        edit_item.new_action('Clear').connect('activated', self.on_clear)

        colors_item = actor.new_action('Color')

        def on_color(action, item, w, color):
            self.draw_widget.color = color
        for c, name in [((255, 0, 0), 'red'), ((0, 255, 0), 'green'),
                        ((0, 0, 255), 'blue'), ((255, 255, 255), 'white')]:
            color_item = colors_item.new_action(name)
            color_item.connect('activated', on_color, c)

        sizes_item = actor.new_action('Size')

        def on_size(action, item, w, size):
            self.draw_widget.radius = size
        for s in [2, 4, 8, 16]:
            size_item = sizes_item.new_action(str(s))
            size_item.connect('activated', on_size, s)

        def on_about(action, item, w):
            yield tichy.Dialog(self.window, "About", "Just a test")
        about_item = actor.new_action('About')
        about_item.connect('activated', on_about)

        self.draw_widget = DrawingWidget(vbox, Vect(480, 480))

        gui.Spring(vbox, axis=1)

        yield tichy.Wait(frame, 'back')

    def on_save(self, action, item, w):
        service = tichy.Service('FileBrowser')
        path = yield service.get_save_path(self.window, 'untitled')
        logger.info("saving drawing to %s", path)
        try:
            pygame.image.save(self.draw_widget.surface, path)
        except Exception, e:
            logger.error("%s", e)

    def on_load(self, action, item, w):
        service = tichy.Service('FileBrowser')
        path = yield service.get_load_path(self.window)
        logger.info("loading %s", path)
        try:
            self.draw_widget.surface = pygame.image.load(path)
        except Exception, e:
            logger.error("%s", e)

    def on_clear(self, action, item, w):
        self.draw_widget.clear()
