#    Tichy
#    copyright 2008 Guillaume Chereau (charlie@openmoko.org)
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

import dbus
from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)

import tichy

import logging
logger = logging.getLogger('SIM')
logger.setLevel(logging.DEBUG)

class FreeSmartPhoneSim(tichy.Service):
    service = 'SIM'
    
    def __init__(self):
        logger.info("connecting to freesmartphone.GSM dbus interface")
        try:
            # We create the dbus interfaces to org.freesmarphone
            bus = dbus.SystemBus()
            self.gsm = bus.get_object('org.freesmartphone.ogsmd', '/org/freesmartphone/GSM/Device')
            self.gsm_sim = dbus.Interface(self.gsm, 'org.freesmartphone.GSM.SIM')
        except Exception, e:
            logger.warning("can't use freesmartphone GSM : %s", e)
            self.gsm = None
            raise tichy.ServiceUnusable
    
    def get_contacts(self):
        logger.info("Retrieve Phonebook")
        ret = self.gsm_sim.RetrievePhonebook('contacts')
        logger.debug('get contacts : %s', ret)
        ret = [(unicode(s[1]), str(s[2])) for s in ret]
        yield ret
        
        
class TestSim(tichy.Service):
    service = 'SIM'
    
    def get_contacts(self):
        yield [('test', '099872394')]
