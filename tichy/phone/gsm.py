#!/usr/bin/env python
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

__docformat__ = 'reStructuredText'

import logging
logger = logging.getLogger('GSM')

import dbus

import tichy
from tichy.tasklet import WaitDBus
from tichy.phone.call import Call


class GSMService(tichy.Service):

    """GSM Service base class

    signals

        provider-modified(string name)
            emitted when the provider name has been  modified

        incoming-call(call)
            indicate an incoming call. Pass the `Call` object
    """

    def register(self):
        """This must return a Tasklet"""
        raise NotImplementedError

    def create_call(self, number):
        """create a new call to a given number"""
        raise NotImplementedError


class FreeSmartPhoneGSM(GSMService):
    """GSMService that uses freesmartphone DBUS API"""

    service = 'GSM'

    def __init__(self):
        logger.info("connecting to freesmartphone.GSM dbus interface")
        try:
            # We create the dbus interfaces to org.freesmarphone
            self.bus = dbus.SystemBus(mainloop=tichy.mainloop.dbus_loop)
            self.ousage = self.bus.get_object(
                'org.freesmartphone.ousaged',
                '/org/freesmartphone/Usage')
            self.ousage = dbus.Interface(
                self.ousage,
                'org.freesmartphone.Usage')
            self.gsm = self.bus.get_object(
                'org.freesmartphone.ogsmd',
                '/org/freesmartphone/GSM/Device')
            self.gsm_device = dbus.Interface(
                self.gsm,
                'org.freesmartphone.GSM.Device')
            self.gsm_network = dbus.Interface(
                self.gsm,
                'org.freesmartphone.GSM.Network')
            self.gsm_call = dbus.Interface(
                self.gsm,
                'org.freesmartphone.GSM.Call')
            self.gsm.connect_to_signal("Status", self.on_status)
            self.gsm.connect_to_signal("CallStatus", self.on_call_status)
        except Exception, e:
            logger.warning("can't use freesmartphone GSM : %s", e)
            self.gsm = None
            raise tichy.ServiceUnusable

        self.lines = {}
        self.provider = None
        self.network_strength = None
        self.logs = tichy.List()

    def get_provider(self):
        return self.provider

    def register(self, on_step=None):
        """Tasklet that registers on the network

        :Parameters:

            on_step : callback function | None
                a callback function that take a string argument that
                will be called at every step of the registration
                procedure
        """

        def default_on_step(msg):
            pass
        on_step = on_step or default_on_step

        try:
            logger.info("Request the GSM resource")
            on_step("Request the GSM resource")
            yield WaitDBus(self.ousage.RequestResource, 'GSM')
            yield self._turn_on(on_step)
            on_step("Register on the network")
            logger.info("register on the network")
            yield WaitDBus(self.gsm_network.Register)
            yield tichy.Wait(self, 'provider-modified')
        except Exception, e:
            logger.error("Error : %s", e)
            print type(e)
            raise

    def _turn_on(self, on_step):
        logger.info("Check antenna power")
        power = yield WaitDBus(self.gsm_device.GetAntennaPower)
        logger.info("antenna power is %d", power)
        if power:
            yield None
        logger.info("turn on antenna power")
        on_step("Turn on antenna power")
        for i in range(3):
            try:
                yield WaitDBus(self.gsm_device.SetAntennaPower, True)
            except dbus.exceptions.DBusException, e:
                if e.get_dbus_name() != \
                        'org.freesmartphone.GSM.SIM.AuthFailed':
                    raise
                # We ask for the PIN
                yield self._ask_pin()

    def _ask_pin(self):
        window = tichy.Service("WindowsManager").get_app_parent()
        editor = tichy.Service('TextEdit')
        pin = yield editor.edit(window, name="Enter PIN",
                                input_method='number')
        yield tichy.Service('SIM').send_pin(pin)

    def on_call_status(self, call_id, status, properties):
        logger.info("call status %s %s %s", id, status, properties)
        call_id = int(call_id)
        status = str(status)

        if status == 'incoming':
            logger.info("incoming call")
            # XXX: should use an assert, but it doesn't work on neo :O
            if call_id in self.lines:
                logger.warning("WARNING : line already present %s %s",
                               call_id, self.lines)
                # XXX : I just ignore the message, because the
                # framework send it twice !! Bug in the framework ?
                return
                # raise Exception("call already present")
            peer_number = str(properties.get('peer', "Unknown"))

            call = self.create_call(peer_number, direction='in')
            call.__id = call_id
            self.lines[call_id] = call

            assert call_id in self.lines
            self.emit('incoming-call', call)

        elif status == 'outgoing':
            self.lines[call_id].outgoing()
        elif status == 'active':
            self.lines[call_id].active()
        elif status == 'release':
            self.lines[call_id].released()
            del self.lines[call_id]
        else:
            logger.warning("Unknown status : %s", status)

    def on_status(self, status):
        logger.debug("status %s", status)
        if 'provider' in status:
            provider = str(status['provider'])
            if provider != self.provider:
                self.provider = provider
                self.emit('provider-modified', self.provider)
        if 'strength' in status:
            strength = int(status['strength'])
            if strength != self.network_strength:
                self.network_strength = strength
                self.emit('network-strength', self.network_strength)

    def create_call(self, number, direction='out'):
        logger.info("create call %s" % number)
        call = Call(number, direction=direction)
        self.logs.append(call)
        return call

    def initiate(self, call):
        logger.info("initiate call to %s", str(call.number))
        call_id = int(self.gsm_call.Initiate(str(call.number), "voice"))
        logger.info("call id : %d", call_id)
        self.lines[call_id] = call
        # TODO: mabe not good idea to store this in the call itself
        call.__id = call_id

    def activate(self, call):
        logger.info("activate call %s", str(call.number))
        self.gsm_call.Activate(call.__id)

    def release(self, call):
        logger.info("release call %s", str(call.number))
        self.gsm_call.Release(call.__id)


class TestGsm(tichy.Service):
    """Fake service that can be use to test without GSM drivers"""

    service = 'GSM'

    def __init__(self):
        self.logs = tichy.List([Call('0478657392'), Call('93847298')])

    def register(self, on_step=None):

        def default_on_step(msg):
            pass
        on_step = on_step or default_on_step

        logger.info("Turn on antenna power")
        on_step("Turn on antenna power")
        logger.info("Register on the network")
        on_step("Register on the network")
        self.emit('provider-modified', "Charlie Telecom")
        yield None

    def create_call(self, number, direction='out'):
        return Call(number, direction=direction)

    def initiate(self, call):

        def after_a_while():
            call.active()
        tichy.mainloop.timeout_add(1000, after_a_while)

    def release(self, call):

        def after_a_while():
            call.released()
        tichy.mainloop.timeout_add(1000, after_a_while)

    def get_provider(self):
        return 'Charlie Telecom'
