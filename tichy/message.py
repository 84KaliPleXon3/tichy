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

"""Message module"""

import logging
logger = logging.getLogger('Messages')

import tichy


class Message(tichy.Item):
    """Base class for all messages
    """

    def __init__(self, peer, text, direction, status=None):
        """Create a new contact

        :Parameters:

        - peer : the number / contact of the peer of the message. Its
          __repr__ method will be used as the item's name.

        - text : the text of the message.

        - direction : the direction of the message. Cab be 'in' or
          'out'.

        - status : the status of the message. Can be 'read' or
          'unread'. If set to None, incoming message will have
          'unread' status and outgoing message will have 'read' status
        """
        self.peer = tichy.TelNumber.as_text(peer)
        self.text = tichy.Text.as_text(text)
        assert direction in ['in', 'out'], direction
        self.direction = direction
        self.status = status or direction == 'out' and 'read' or 'unread'
        assert self.status in ['read', 'unread'], status

    def get_text(self):
        return tichy.Text("%s" % str(self.peer))

    def read(self):
        if self.status == 'read':
            return
        self.status = 'read'
        self.emit('read')

    def create_actor(self):
        """Return an actor on this message"""
        actor = super(Message, self).create_actor()
        view_action = actor.new_action("View")

        def on_view_action(action, msg, view):
            self.read()
            yield self.edit(view.window)

        view_action.connect('activated', on_view_action)
        return actor


class MessagesService(tichy.Service):
    """The service that stores all the messages
    """

    service = 'Messages'

    def __init__(self):
        self.outbox = tichy.List()
        self.inbox = tichy.List()
        # Prepare the future notification
        self.notification_icon = tichy.Image(self.path('pics/message.png'),
                                             (32, 32))
        self.notification = None

    def add_to_inbox(self, msg):
        logger.info("Add to inbox : %s", msg)
        assert(isinstance(msg, Message))
        self.inbox.insert(0, msg)
        msg.connect('read', self.on_message_read)
        self._update()

    def add_to_outbox(self, msg):
        logger.info("Add to outbox : %s", msg)
        assert(isinstance(msg, Message))
        self.outbox.insert(0, msg)

    def on_message_read(self, msg):
        self._update()

    def _update(self):
        """Update the notification according to the number of unread messages
        in the inbox.
        """
        nb_unread = len([m for m in self.inbox if m.status == 'unread'])
        logger.debug("%d unread messages", nb_unread)
        if nb_unread == 0 and self.notification:
            self.notification.release()
            self.notification = None
        elif nb_unread > 0 and not self.notification:
            notifications = tichy.Service('Notifications')
            self.notification = notifications.notify(
                "You have a new message", self.notification_icon)
        elif nb_unread > 0 and self.notification:
            self.notification.msg = "You have %d unread messages" % nb_unread
