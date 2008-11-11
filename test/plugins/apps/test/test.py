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


class Test(tichy.Application):

    name = 'Test'
    icon = None
    category = 'general' # So that we see the app in the launcher

    def run(self, parent):
        self.window = gui.Window(parent)
        frame = self.view(self.window, back_button=True)
        vbox = gui.Box(frame, axis=1, expand=True)

        button = gui.Button(vbox)
        gui.Label(button, "fake SMS")
        button.connect('clicked', self.on_fake_sms)

        # Wait until the quit button is clicked
        yield tichy.Wait(frame, 'back')
        self.window.destroy()

    def on_fake_sms(self, b):
        sms_service = tichy.Service('SMS', 'Test')
        sms_service.fake_incoming_message("hello")
