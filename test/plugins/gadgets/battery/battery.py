
import time

import tichy
from tichy import gui

import logging
logger = logging.getLogger('gadg.battery')

class Battery(tichy.Gadget):
    name = 'Battery'
    def run(self, window):
        self.image = tichy.Image(self.path('battery0.png'), (32, 32))
        self.image.view(window)
        self.capacity = None
        tichy.mainloop.timeout_add(5000, self.on_timer)
        yield None
        
    def on_timer(self):
        # We get the battery status
        logger.debug("Update battery status")
        try:
            status = open("/sys/devices/platform/bq27000-battery.0/power_supply/bat/status").read().strip()
            if status == 'Charging':
                self.image.path = self.path('charging.png')
                return True

            capacity = int(open("/sys/devices/platform/bq27000-battery.0/power_supply/bat/capacity").read())
            if capacity == self.capacity:
                return 0
            # Let suppose the capacity goes from 0 to 100 (???)
            index = capacity * 4 / 100
            assert index > 0 and index <= 4, index
            self.image.path = self.path('battery%d.png' % index)
        except IOError:
            pass
        return True
