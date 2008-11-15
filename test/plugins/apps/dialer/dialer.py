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

import logging
logger = logging.getLogger('App.Dialer')

import tichy
from tichy import gui
from tichy.gui import Vect


class Keyboard(gui.Table):
    """Special widget for dialer keyboard

    It emit the 'key-pressed' signal.
    """

    def __init__(self, parent, **kargs):
        super(Keyboard, self).__init__(parent, axis=1, nb=3, spacing=0,
                                       **kargs)
        self.keys = []
        for i, line in enumerate(['123', '456', '789', '*0+']):
            for j, key in enumerate(line):
                w = gui.Button(self, min_size=Vect(144, 72),
                               optimal_size=Vect(144, 72))
                w.connect('clicked', self.on_click, key)
                gui.Label(w, key)
                self.keys.append(w)

    def on_click(self, w, k):
        self.emit('key-pressed', k)


class DialerApp(tichy.Application):

    name = 'Dialer'
    icon = 'icon.png'
    category = 'main'

    def run(self, parent, text=""):
        if isinstance(text, str):
            text = tichy.Text(text)
        self.window = gui.Window(parent, modal=True)
        frame = self.view(self.window, back_button=True)

        vbox = gui.Box(frame, axis=1, expand=True)
        self.text = text
        self.text.view(vbox, editable=False)
        k = Keyboard(vbox, expand=True)
        k.connect('key-pressed', self.on_key)

        hbox = gui.Box(vbox, axis=0)

        call_button = gui.Button(hbox)
        call_button.connect('clicked', self.on_call)
        gui.Label(call_button, "Call")

        del_button = gui.Button(hbox)
        gui.Label(del_button, "Del")
        del_button.connect('clicked', self.on_del)

        # quit_item = frame.actor.new_action('Quit')

        yield tichy.Wait(frame, 'back')
        self.window.destroy()   # Don't forget to close the window

    def on_key(self, w, k):
        self.text.value += k  # The view will automatically be updated

    def on_del(self, w):
        self.text.value = self.text.value[:-1]

    def on_call(self, b):
        yield Caller(self.window, self.text.value)


# TODO: ??? make the Caller app better, using John idea : we define
#       for every call status the status of the gui.  Then we just
#       wait for status change and set up the gui in consequence It
#       means we have an automaton with a single state, much simpler
#       to deal with that what we have now


class Caller(tichy.Application):
    """This is the application that deal with the calling sequence
    """

    def run(self, parent, number):
        """number can be a string or an incoming call object"""
        # We open a new window for a call
        self.window = gui.Window(parent)
        frame = self.view(self.window, title='Dialer')
        vbox = gui.Box(frame, axis=1)

        text = tichy.Text("Initialization")
        text.view(vbox)

        try:
            gsm_service = tichy.Service('GSM')
            # The case when we have an incoming call
            if isinstance(number, tichy.phone.Call):
                call = number

                text.value = "incoming %s" % call.number
                answer_button = gui.Button(vbox)
                gui.Label(answer_button, 'Answer')

                def on_answer(b):
                    b.destroy()
                    call.activate()
                answer_button.connect('clicked', on_answer)
            else:   # If not it means we want to initiate the call first
                call = gsm_service.create_call(number)
                call.initiate()
                text.value = "initiating %s" % number

            button = gui.Button(vbox)
            button_label = gui.Label(button, 'Cancel')
            i, args = yield tichy.WaitFirst(tichy.Wait(button, 'clicked'),
                                            tichy.Wait(call, 'activated'))
            if i == 1: # activated:
                # Now the call is active
                text.value = "calling %s" % call.number
                button_label.text = "hang up"
                i, args = yield tichy.WaitFirst(
                    tichy.Wait(button, 'clicked'),
                    tichy.Wait(call, 'released'))

            if call.status not in ['released', 'releasing']:
                text.value = "releasing %s" % call.number
                call.release()
                yield tichy.Wait(call, 'released')

        except Exception, e:
            import traceback
            logger.error("%s, %s", e, traceback.format_exc())
            yield tichy.Dialog(self.window, "Error", e.message)

        self.window.destroy()


class MyCallerService(tichy.Service):

    service = 'Caller'

    def call(self, parent, number):
        return Caller(parent, number)
