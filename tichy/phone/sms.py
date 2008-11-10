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

import logging
logger = logging.getLogger('SMS')

class SMS(tichy.Message):
    def __init__(self, number, text, direction='out'):
        super(SMS, self).__init__(number, text, direction)

    def __get_number(self):
        return self.peer
    number = property(__get_number)

    def send(self):
        sms_service = tichy.Service('SMS')
        yield sms_service.send(self)
    def create_actor(self):
        """Return an actor on this sms message"""
        actor = super(SMS, self).create_actor()
        view_action = actor.new_action("View")
        def on_view_action(action, sms, view):
            sms_editor = tichy.Service('EditSMS')
            self.read()         # so that the message update its status
            yield sms_editor.edit(sms, view.window)
        view_action.connect('activated', on_view_action)
        return actor

class FreeSmartPhoneSMS(tichy.Service):
    service = 'SMS'

    def __init__(self):
        logger.info("connecting to freesmartphone.GSM dbus interface")
        try:
            # We create the dbus interfaces to org.freesmarphone
            bus = dbus.SystemBus()
            gsm = bus.get_object('org.freesmartphone.ogsmd', '/org/freesmartphone/GSM/Device')
            self.sim_iface = dbus.Interface(gsm, 'org.freesmartphone.GSM.SIM')
            logger.info("Listening to incoming SMS")
            self.sim_iface.connect_to_signal("IncomingStoredMessage", self.on_incoming_message)
        except Exception, e:
            logger.warning("can't use freesmartphone SMS : %s", e)
            self.sim_iface = None
            raise tichy.ServiceUnusable

    def update(self):
        logger.info("update sms inbox")
        status = yield tichy.tasklet.WaitDBus(self.sim_iface.GetSimReady)
        status = yield tichy.tasklet.WaitDBus(self.sim_iface.GetAuthStatus)
        messages = yield tichy.tasklet.WaitDBus(self.sim_iface.RetrieveMessagebook, "all")
        logger.info("found %s messages into sim", len(messages))

        messages_service = tichy.Service('Messages')
        for msg in messages:
            id, status, number, text = msg
            sms = self.create(str(number), unicode(text), 'in')
            messages_service.add_to_inbox(sms)

    def create(self, number='', text='', direction='out'):
        """create a new sms instance"""
        number = tichy.phone.TelNumber(number)
        text = tichy.Text(text)
        return SMS(number, text)

    def send(self, sms):
        logger.info("Storing message to %s", sms.peer)
        message_id = yield tichy.tasklet.WaitDBus(self.sim_iface.StoreMessage, str(sms.peer), unicode(sms.text), {})
        logger.info("Done, id : %s", message_id)
        logger.info("Sending message")
        yield tichy.tasklet.WaitDBus(self.sim_iface.SendStoredMessage, message_id)
        logger.info("Done")
        # We store a copy cause we don't want to modify the stored sms.
        logger.info("Store message into outbox")
        sms = SMS(sms.peer, sms.text, 'out')
        tichy.Service('Messages').add_to_outbox(sms)

    def on_incoming_message(self, index):
        logger.info("Incoming message %d", index)
        # TODO: finish it

class TestSms(tichy.Service):
    service = 'SMS'
    name = 'Test'

    def __init__(self):
        # Add a test message
        self.create('0123456789', 'Hello')

    def create(self, number='', text='', direction='out'):
        number = tichy.phone.TelNumber(number)
        text = tichy.Text(text)
        return SMS(number, text, direction)

    def update(self):
        yield None

    def send(self, sms):
        logger.info("Sending message to %s", sms.number)
        tichy.Service('Messages').add_to_outbox(sms)
        yield None

    def fake_incoming_message(self, msg):
        logger.info("Incoming message %d", 0)
        sms = self.create('0123456789', msg, 'in')
        tichy.Service('Messages').add_to_inbox(sms)
