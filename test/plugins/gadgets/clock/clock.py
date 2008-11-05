
import time 

import tichy
from tichy import gui

class Clock(tichy.Gadget):
    name = 'Clock'
    def run(self, window):
        self.text = tichy.Text('')
        # XXX: we shouldn't have to guess the size here !
        self.text.view(window, optimal_size = gui.Vect(32 * 8, 64))
        tichy.mainloop.timeout_add(500, self.on_timeout)
        yield None
        
    def on_timeout(self):
        self.text.value = time.strftime("%H:%M",time.localtime())
        return True
