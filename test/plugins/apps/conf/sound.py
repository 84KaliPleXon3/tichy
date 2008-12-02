#    Tichy
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

import logging
logger = logging.getLogger('app.dict')

import tichy
import tichy.gui as gui


# XXX: Use a special widget for integer controls.  We should have a
#      tichy.Int item, and then the designer can decide how we show
#      the control on screen, exactly like it works with text.


class VolumeItem(tichy.Item):

    def __init__(self, name):
        self.name = name
        self.text = tichy.Text('')
        self._update()

    def view(self, parent):
        box = gui.Box(parent, axis=0)
        gui.Label(box, self.name)
        self.text.view(box)
        inc = gui.Button(box)
        gui.Label(inc, '+')
        inc.connect('clicked', self._on_inc)
        dec = gui.Button(box)
        gui.Label(dec, '-')
        dec.connect('clicked', self._on_dec)
        return box

    def _on_inc(self, *args):
        tichy.Service('Sound').volume += 5
        self._update()

    def _on_dec(self, *args):
        tichy.Service('Sound').volume -= 5
        self._update()

    def _update(self):
        value = tichy.Service('Sound').volume
        self.text.value = '%d' % value


class SoundConf(tichy.Application):

    name = 'Sound'
    icon = 'sound.png'

    def run(self, window):
        frame = self.view(window, back_button=True)

        vbox = gui.Box(frame, axis=1, expand=True)

        master = VolumeItem('master')
        master.view(vbox)

        yield tichy.Wait(frame, 'back')


class SoundSetting(tichy.Service):
    """Service that will start the sound config app

    This is usefull for all the applications that need fast way to set
    the volume (caller, media player, etc...)
    """

    service = 'SoundsSetting'

    def start(self, window):
        """Return a `Tasklet` that will allow user to set the sound volume

        :Parameters:

            window : gui.Widget
                The parent window where we can start the application

        :Returns: `tasklet`
        """
        return SoundConf(window)
