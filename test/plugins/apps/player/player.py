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

import gst
import os

import tichy
import tichy.gui as gui

import logging
logger = logging.getLogger('App.Player')
logger.setLevel(logging.DEBUG)


class Player(tichy.Application):

    name = "Player"
    icon = 'play.png'
    category = 'main'

    player = None # The gstreamer player instance

    def run(self, parent):
        self.window = gui.Window(parent, modal=True)
        frame = self.view(self.window, back_button=True)

        vbox = gui.Box(frame, axis=1)

        self.file_name = tichy.Text("No file")
        self.file_name.view(vbox)

        self.x_window = gui.XWindow(vbox)

        self.status_name = tichy.Text("")
        self.status_name.view(vbox)

        # We put a few buttons
        box = gui.Box(vbox, axis=0)
        play_button = gui.Button(box, optimal_size=gui.Vect(96, 96))
        tichy.Image(self.path('play.png')).view(play_button)
        pause_button = gui.Button(box, optimal_size=gui.Vect(96, 96))
        tichy.Image(self.path('pause.png')).view(pause_button)
        stop_button = gui.Button(box, optimal_size=gui.Vect(96, 96))
        tichy.Image(self.path('stop.png')).view(stop_button)
        open_button = gui.Button(box, optimal_size=gui.Vect(96, 96))
        tichy.Image(self.path('open.png')).view(open_button)

        stop_button.connect('clicked', self.on_stop)
        play_button.connect('clicked', self.on_play)
        pause_button.connect('clicked', self.on_pause)
        open_button.connect('clicked', self.on_open)

        frame.actor.new_action("Open").connect('activated', self.on_open)
        yield tichy.Wait(frame, 'back')
        self.window.destroy()

    def on_sync_message(self, bus, message):
        logger.debug("sync message : %s", message)
        if message.structure is None:
            return
        message_name = message.structure.get_name()
        if message_name == "prepare-xwindow-id":
            logger.debug("prepare-xwindow-id")
            imagesink = message.src
            imagesink.set_property("force-aspect-ratio", True)
            try:
                imagesink.set_xwindow_id(self.x_window.id)
            except Exception:
                logger.error("can't prepare-xwindow")

    def create_player(self):
        player = gst.element_factory_make("playbin", "player")
#        fakesink = gst.element_factory_make("fakesink", "fakesink")
#        player.set_property("video-sink", fakesink)
        bus = player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("sync-message::element", self.on_sync_message)
        return player

    def play(self, filepath=None):
        # filepath = "/home/root/test.ogg"
        if not Player.player:
            logger.debug("Creating player")
            Player.player = self.create_player()
        if filepath:
            self.stop()
            Player.player.set_property("uri", "file://" + filepath)
            self.file_name.value = os.path.basename(filepath)

        logger.debug("Start playing")
        Player.player.set_state(gst.STATE_PLAYING)
        self.status_name.value = "play"

    def stop(self):
        if Player.player:
            Player.player.set_state(gst.STATE_READY)
        self.status_name.value = "stop"

    def pause(self):
        if Player.player:
            Player.player.set_state(gst.STATE_PAUSED)
        self.status_name.value = "paused"

    def on_stop(self, b):
        self.stop()

    def on_play(self, b):
        self.play()

    def on_pause(self, b):
        self.pause()

    def on_open(self, *args):
        # Unfortunately The XWindow won't hide by itself
        self.x_window.hide()
        service = tichy.Service('FileBrowser')
        path = yield service.get_load_path(self.window)
        self.x_window.show()
        logger.info("opening %s", path)
        self.play(path)
