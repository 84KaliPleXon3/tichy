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
import tichy.gui as gui


class SettingItem(tichy.Item):

    def __init__(self, name):
        self.name = name


class ScreenLockConf(tichy.Application):

    name = 'Screen Lock'

    def run(self, parent):
        self.srvc = tichy.Service('ScreenLock')
        self.window = gui.Window(parent)
        frame = self.view(self.window, back_button=True)

        vbox = gui.Box(frame, axis=1, expand=True)

        self.current_text = tichy.Text("Current : %s" % self.srvc.pattern)
        self.current_text.view(vbox)

        patterns_list = tichy.ActorList()
        # We get all the patterns services
        for pattern_name in self.srvc.patterns:
            pattern = SettingItem(pattern_name)
            actor = tichy.Actor(pattern)
            use_action = actor.new_action('Use')
            use_action.connect('activated', self.on_use_pattern)
            patterns_list.append(actor)

        patterns_list.view(vbox)

        yield tichy.Wait(frame, 'back')
        self.window.destroy()

    def on_use_pattern(self, action, pattern, window):
        self.srvc.pattern = pattern.name
        self.current_text.value = "Current : %s" % pattern
