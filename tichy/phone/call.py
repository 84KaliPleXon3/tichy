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


class Call(tichy.Item):

    def __init__(self, number, direction='out'):
        self.number = tichy.TelNumber(number)
        self.direction = direction
        self.status = 'inactive'

    def get_text(self):
        return self.number.get_text()

    def initiate(self):
        gsm_service = tichy.Service('GSM')
        gsm_service.initiate(self)
        self.status = 'initiating'
        self.emit(self.status)

    def release(self):
        if self.status in ['releasing', 'released']:
            return
        gsm_service = tichy.Service('GSM')
        gsm_service.release(self)
        self.status = 'releasing'
        self.emit(self.status)

    def activate(self):
        gsm_service = tichy.Service('GSM')
        gsm_service.activate(self)
        self.status = 'activating'
        self.emit(self.status)

    def outgoing(self):
        self.status = 'outgoing'
        self.emit('outgoing')

    def active(self):
        self.status = 'active'
        self.emit('activated')

    def released(self):
        self.status = 'released'
        self.emit('released')
