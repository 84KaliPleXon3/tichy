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
    def __init__(self, service, msg, icon=None):
        super(Notification, selfg).__init__()
        self.service = service
        self.msg = msg
        self.icon = icon

    def release(self):
        """To be called when the notification can be removed"""
        self.service._remove(self)

class Notifications(tichy.Service):
    """Notification service

    This service can be used by any plugin that wants to notify the
    user about something, but doesn't want to open a new window for
    that. That is useful for things like notify incoming SMS, etc.

    The system can see all the pending notifications, and also be
    notified whenever a new notification arrives.

    :Signals:

    - new-notification(notification) : emmited when a new notification
      arrives
    """
    service = 'Notifications'

    def __init__(self):
        self.notifications = []

    def notify(self, msg, icon=None):
        """add a new notification

        :Parameters:

        - msg : the message of the notification
        
        - icon : an optional icon for the notification
        """
        logger.info("New notification : %s", msg)
        notification = Notification(msg, icon)
        self.notifications.append(notification)
        self.emit('new-notification', notification)

    def _remove(self, notification):
        self.notifications.remove(notification)
