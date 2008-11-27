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


"""Persistance module"""

import os
import yaml

import logging
logger = logging.getLogger('persistance')


class Persistance(object):
    """Use this class to save and load data from file"""

    base_path = os.path.expanduser('~/.tichy/')

    def __init__(self, path):
        self.path = path

    def _open(self, mod='r'):
        path = os.path.join(self.base_path, self.path)
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
            os.makedirs(dir)
        try:
            return open(path, mod)
        except IOError, e:
            logger.warning("can't open file : %s", e)
            raise

    def save(self, data):
        file = self._open('w')
        file.write(yaml.safe_dump(data, default_flow_style=False))

    def load(self):
        file = self._open()
        return yaml.safe_load(file)
