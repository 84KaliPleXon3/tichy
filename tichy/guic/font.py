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

import pygame
import pygame.font


class Font(object):

    def __init__(self, name=None, size=32):
        name = name or 'arplumingtwmbe'
        file = pygame.font.match_font(name)
        self.font = pygame.font.Font(file, size)

    def render_line(self, text, color=None):
        # We use a little trick to add a border to the text
        border = self.font.render(text, True, (64, 64, 64))
        text = self.font.render(text, True, (255, 255, 255))
        ret = pygame.Surface(text.get_rect().inflate(2, 2).size, 0, text)
        for x in (0, 2):
            for y in (0, 2):
                ret.blit(border, (x, y))
        ret.blit(text, (1, 1))
        return ret.convert_alpha()

    def render(self, text, color=None, length=None):
        lines = self.split(text, length)
        surfs = [self.render_line(line) for line in lines]
        height = self.font.get_height()
        rects = [surf.get_rect().move(0, height * i) \
                     for i, surf in enumerate(surfs)]
        rect = pygame.Rect(0, 0, 0, 0).unionall(rects)
        surf = pygame.Surface(rect.size, pygame.SRCALPHA, 32).convert_alpha()
        for s, r in zip(surfs, rects):
            surf.blit(s, r)
        return surf

    def split(self, text, length=None):
        # For the moment we use a very stupid way of doing it...
        ret = []
        i = 0
        while text:
            i += 1
            if i > len(text):
                ret.append(text)
                break
            line = text[:i]
            if line[-1] == '\n':
                ret.append(line[:-1])
                text = text[i:]
                i = 0
                continue
            if length and self.font.size(line)[0] >= length:
                ret.append(line[:-1])
                text = text[i-1:]
                i = 0
                continue
        return ret
