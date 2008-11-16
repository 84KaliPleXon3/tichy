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

import tichy
import tichy.gui as gui

import logging
logger = logging.getLogger('app.reader')


class Reader(tichy.Application):
    """Simple application that can read a text file using espeak
    """

    name = 'Reader'
    category = 'main/chinese'

    def run(self, window):
        """run the app

        The screen is spearated in on part showing the chunk of the
        text that can be read, and one part showing the possible
        actions : read, or get next chunk.

        The application also define a few actions to open a file, set
        the speed of the voice, etc.
        """
        self.file = None
        self.speed = 120
        self.voice = 'm1'

        self.window = gui.Window(window, modal=True)
        frame = self.view(self.window, back_button=True)

        # create the app menu
        actor = frame.actor

        open_item = actor.new_action("Open")
        open_item.connect('activated', self.on_open)

        speed_item = actor.new_action("Speed")
        for speed in [50, 120, 170, 300]:
            item = speed_item.new_action("%d" % speed)
            item.connect('activated', self.on_set_speed, speed)

        voice_item = actor.new_action("Voice")
        for voice in ['m1', 'm2', 'f1', 'f2']:
            item = voice_item.new_action("%s" % voice)
            item.connect('activated', self.on_set_voice, voice)

        # Show the text zone
        vbox = gui.Box(frame, axis=1, expand=True)
        self.text = tichy.Text('')
        self.text.view(vbox, expand=True)
        hbox = gui.Box(vbox, axis=0)

        # Create the buttons
        read_button = gui.Button(hbox)
        gui.Label(read_button, "Read")
        read_button.connect('clicked', self.on_read)

        next_button = gui.Button(hbox)
        gui.Label(next_button, "Next")
        next_button.connect('clicked', self.on_next)

        # Wait till we quit
        yield tichy.Wait(frame, 'back')
        self.window.destroy()

    def on_set_speed(self, action, item, w, speed):
        logger.info("set speed to %d", speed)
        self.speed = speed

    def on_set_voice(self, action, item, w, voice):
        logger.info("set voice to %s", voice)
        self.voice = voice

    def on_open(self, action, item, view):
        service = tichy.Service('FileBrowser')
        path = yield service.get_load_path(self.window)
        logger.info("open file %s", path)
        try:
            # XXX: add checks that the file is a text file !
            file = open(path)
            self.open(file)
        except Exception, e:
            logger.error("%s", e)

    def open(self, file):
        self.file = file
        self.next()

    def on_next(self, button):
        if not self.file:
            return
        self.next()

    def next(self):
        # TODO: optimize this...
        line = ''
        while True:
            c = self.file.read(1)
            line += c
            if not c or c == '.':
                break
        # Make sure we handle utf-8
        line = line.decode('utf-8').strip()
        logger.info('read %s', repr(line))
        self.text.value = line

    def on_read(self, button):
        text = unicode(self.text)
        try:
            import subprocess
            espeak = 'espeak -s%d -v+%s --stdout' % \
                (self.speed, self.voice)
            cmd = "echo '%s' | %s | aplay" % (text, espeak)
            logger.info("bash : %s", cmd)
            subprocess.Popen(cmd, shell=True)
        except Exception, e:
            logger.error("can't use espeak : %s" % e)
