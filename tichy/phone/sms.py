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

class SMS(tichy.Item):
    def __init__(self, number, text):
        self.number = number
        self.text = text
    def get_text(self):
        return tichy.Text("%s" % str(self.number))
    def send(self):
        sms_service = tichy.Service('SMS')
        yield sms_service.send(self)
    def create_actor(self):
        """Return an actor on this sms message"""
        actor = super(SMS, self).create_actor()
        view_action = actor.new_action("View")
        def on_view_action(action, sms, view):
            sms_editor = tichy.Service('EditSMS')
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
            self.sim_iface.connect_to_signal("IncomingMessage", self.on_incoming_message)
        except Exception, e:
            logger.warning("can't use freesmartphone GSM : %s", e)
            self.sim_iface = None
            raise tichy.ServiceUnusable
        self.outbox = tichy.List()
        self.inbox = tichy.List()
        
    def update(self):
        logger.info("update sms inbox")
        status = yield tichy.tasklet.WaitDBus(self.sim_iface.GetSimReady)
        status = yield tichy.tasklet.WaitDBus(self.sim_iface.GetAuthStatus)
        messages = yield tichy.tasklet.WaitDBus(self.sim_iface.RetrieveMessagebook, "all")
        logger.info("found %s messages into sim", len(messages))
        self.inbox.clear()
        for msg in messages:
            id, status, number, text = msg
            self.inbox.append(self.create(str(number), unicode(text)))
            
    def create(self, number = '', text = ''):
        number = tichy.phone.TelNumber(number)
        text = tichy.Text(text)
        return SMS(number, text)
            
    def send(self, sms):
        logger.info("Storing message to %s", sms.number)
        message_id = yield tichy.tasklet.WaitDBus(self.sim_iface.StoreMessage, str(sms.number), unicode(sms.text))
        logger.info("Done, id : %s", message_id)
        logger.info("Sending message")
        yield tichy.tasklet.WaitDBus(self.sim_iface.SendStoredMessage, message_id)
        logger.info("Done")
        # We store a copy cause we don't want to modify the stored sms.
        logger.info("Store message into outbox")
        self.outbox.append(SMS(sms.number, sms.text))
        
    def on_incoming_message(self, index):
        logger.info("Incoming message %d", index)
        
class TestSms(tichy.Service):
    service = 'SMS'
    
    def __init__(self):
        self.outbox = tichy.List()
        self.outbox.append(self.create('09230984', "A test"))
        self.inbox = tichy.List()
        
    def create(self, number = '', text = ''):
        number = tichy.phone.TelNumber(number)
        text = tichy.Text(text)
        return SMS(number, text)
        
    def update(self):
        yield None
    
    def send(self, sms):
        logger.info("Sending message to %s", sms.number)
        self.outbox.append(SMS(sms.number, sms.text))
        yield None
