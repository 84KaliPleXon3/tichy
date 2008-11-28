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
import tichy.gui as gui

from profiles import ProfilesConf
from phone import PhoneConf
from screenlockconf import ScreenLockConf


class Conf(tichy.Application):

    name = 'Config'
    icon = 'icon.png'
    category = 'main'

    def run(self, window):
        frame = self.view(window, back_button=True)
        vbox = gui.Box(frame, axis=1, expand=True)

        # We create a list of the sub applications actors
        list = tichy.ActorList()
        for app in [ProfilesConf, StyleConf, PhoneConf, ScreenLockConf]:
            actor = app.create_actor()
            list.append(actor)

        list.view(vbox, expand=True)

        # Wait until the quit button is clicked
        yield tichy.Wait(frame, 'back')


class StyleConf(tichy.Application):

    name = 'Style'

    def run(self, window):
        frame = self.view(window, back_button=True)

        vbox = gui.Box(frame, axis=1, expand=True)
        styles = [s.create() for s in tichy.Style.subclasses]

        styles_list = tichy.ActorList()
        for s in styles:
            actor = tichy.Actor(s)
            use_action = actor.new_action('Use')
            use_action.connect('activated', self.on_use_style)
            styles_list.append(actor)
        styles_list.view(vbox)

        yield tichy.Wait(frame, 'back')

    def on_use_style(self, action, style, window):
        screen = window.screen
        screen.style = style
