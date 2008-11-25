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

import dbus
from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)

import tichy
from tichy.tasklet import WaitDBus

import logging
logger = logging.getLogger('SIM')
logger.setLevel(logging.DEBUG)


class SIMContact(tichy.Contact):
    storage = 'SIM'

    def __init__(self, name, tel=None, sim_index=None, **kargs):
        super(SIMContact, self).__init__(name, **kargs)
        self.sim_index = sim_index
        self.icon = 'pics/sim.png'

    @classmethod
    def import_(cls, contact):
        """create a new contact from an other contact)
        """
        assert not isinstance(contact, SIMContact)
        yield SIMContact(contact.name, tel=contact.tel)


class FreeSmartPhoneSim(tichy.Service):

    service = 'SIM'

    def __init__(self):
        logger.info("connecting to freesmartphone.GSM dbus interface")
        try:
            # We create the dbus interfaces to org.freesmarphone
            bus = dbus.SystemBus()
            self.gsm = bus.get_object('org.freesmartphone.ogsmd',
                                      '/org/freesmartphone/GSM/Device')
            self.gsm_sim = dbus.Interface(self.gsm,
                                          'org.freesmartphone.GSM.SIM')
        except Exception, e:
            logger.warning("can't use freesmartphone GSM : %s", e)
            self.gsm = None
            raise tichy.ServiceUnusable

    def get_contacts(self):
        logger.info("Retrieve Phonebook")
        entries = yield WaitDBus(self.gsm_sim.RetrievePhonebook, 'contacts')
        logger.debug('get contacts : %s', entries)
        ret = []
        for entry in entries:
            index = int(entry[0])
            name = unicode(entry[1])
            tel = str(entry[2])
            contact = SIMContact(name, tel=tel, sim_index=index)
            ret.append(contact)
        yield ret


class TestSim(tichy.Service):

    service = 'SIM'

    def get_contacts(self):
        yield [SIMContact('test', tel='099872394', sim_index=0)]
