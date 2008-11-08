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

"""Notification gadget plugin module"""

import tichy
from tichy import gui

import logging
logger = logging.getLogger('Gadget.Notifications')

class Notifications(tichy.Gadget):
    """Notification gadget

    This will show a little icon per active notifications.
    """
    name = 'Notifications'
    def run(self, window):
        """Create a new box for the notifications"""
        self.box = gui.Box(window, axis=0)
        notifications_service = tichy.Service('Notifications')
        notifications_service.connect('new-notification',
                                      self.on_new_notification)
        yield None

    def on_new_notification(self, service, notification):
        """Add the notification icon into the box"""
        logger.info("New Notification %s", notification)
        if notification.icon:
            view = notification.icon.view(self.box)
            notification.connect('released',
                                 self.on_notification_released, view)

    def on_notification_released(self, notification, view):
        """Remove the notification icon"""
        logger.info("release notification %s", notification)
        view.destroy()
