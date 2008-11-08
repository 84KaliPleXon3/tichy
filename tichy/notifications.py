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

"""Notifications module"""

import logging
logger = logging.getLogger('notifications')

import tichy

class Notification(tichy.Item):
    """Notification class

    Notifications can be used by plugin to notify the user of an event
    or a condition. A typical example is to signal an unread message.

    The plugin should use the 'Notifications' service to create new
    notifications.

    Signals:

    - released : emitted when the notification is released and
      shouldn't be taken care of anymore.
    """
    def __init__(self, service, msg, icon=None):
        super(Notification, self).__init__()
        self.service = service
        self.msg = msg
        self.icon = icon

    def __repr__(self):
        return str(self.msg)

    def notify(self):
        """"Notify the notification, if it is not already the case"""
        if self.service.notifications:
            return
        self.service._add(self)

    def release(self):
        """To be called when the notification can be removed"""
        if self not in self.service.notifications:
            return
        self.service._remove(self)
        self.emit('released')

class Notifications(tichy.Service):
    """Notification service

    This service can be used by any plugin that wants to notify the
    user about something, but doesn't want to open a new window for
    that. That is useful for things like notify incoming SMS, etc.

    The system can see all the pending notifications, and also be
    notified whenever a new notification arrives.

    :Signals:

    - new-notification(notification) : emitted when a new notification
      arrives
    """
    service = 'Notifications'

    def __init__(self):
        self.notifications = []

    def create(self, msg, icon=None):
        """Create a new initially disabled notification

        :Parameters:

        - msg : the message of the notification

        - icon : an optional icon for the notification
        """
        return Notification(self, msg, icon)

    def notify(self, msg, icon=None):
        """add a new notification

        :Parameters:

        - msg : the message of the notification
        
        - icon : an optional icon for the notification
        """
        notification = self.create(msg, icon)
        notification.notify()

    def _add(self, notification):
        self.notifications.append(notification)
        logger.info("Notify : %s", notification)
        self.emit('new-notification', notification)

    def _remove(self, notification):
        logger.info("Remove : %s", notification)
        self.notifications.remove(notification)
