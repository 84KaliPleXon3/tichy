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

import time

import tichy
from tichy import gui

import logging
logger = logging.getLogger('Gadget.GSM')


class GSM(tichy.Gadget):
    """Perform some GSM init and show the provider
    """

    name = 'GSM'

    def run(self, window):
        # We register into gsm
        gsm_status = tichy.Text('...')
        gsm_status.view(window)

        def on_step(msg):
            gsm_status.value = msg

        def on_provider_modified(service, provider):
            on_step(provider)

        gsm_service = tichy.Service('GSM')
        sim_service = tichy.Service('SIM')
        sms_service = tichy.Service('SMS')
        gsm_service.connect('provider-modified', on_provider_modified)
        try:
            # start the registration process
            yield gsm_service.register(on_step)
        # Note : That is a little hackish, I should only filter GSM errors
        except Exception, e:
            logger.error("Error: %s", e)
            gsm_status.value = 'GSM Error'

        try:
            gsm_status.value = 'Retreive Contacts'
            # Get the contacts from the sim
            contacts = yield sim_service.get_contacts()
            contacts_service = tichy.Service('Contacts')
            for (name, tel) in contacts:
                contact = contacts_service.create(name, source='sim')
                contact['tel'] = tichy.phone.TelNumber(tel)
        except Exception, e:
            logger.error("Error: %s", e)
            gsm_status.value = 'SIM Error'
        gsm_status.value = gsm_service.get_provider() or "No GSM"


class NetworkStatus(tichy.Gadget):
    """Monitor the GSM network status.

    This will show a little icon representing the strenght of the
    signal.
    """

    name = 'Network'

    def run(self, window):
        image = tichy.Image(self.path('network0.png'), (32, 32))
        image.view(window)

        gsm_service = tichy.Service('GSM')

        def on_network_strength(gsm, strength):
            # We assume the strenght can go from 0 to 100 (is it true
            # ?).  The images index go from 0 to 4
            index = strength * 4 / 100
            assert index >= 0 and index <= 4
            image.path = self.path('network%d.png' % index)

        gsm_service.connect('network-strength', on_network_strength)

        yield None
