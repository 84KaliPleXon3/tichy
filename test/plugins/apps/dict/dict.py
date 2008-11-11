# -*- coding: utf-8 -*-
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

import os
import bisect

import tichy
import tichy.gui as gui

import logging
logger = logging.getLogger('app.dict')


class Entrie(object):

    def __init__(self, chinese, pinying, translations):
        self.chinese = chinese
        self.pinying = pinying
        self.translations = translations

    def unicode(self):
        return u"%s (%s): %s" % (self.chinese, self.pinying,
                                 "; ".join(self.translations))


class Dict(object):

    def __init__(self, path):
        # All the dicts are sorted so that we can use bisect to find
        # element quickly We only read the lines of the dictionaries
        # and don't try to prcess them before we actually need them
        # otherwise it takes too much time.
        logger.info("read entries")
        file = open(os.path.join(path, 'dict.txt'), 'r')
        self.entries = file.readlines()
        logger.info("%d entries read", len(self.entries))

        logger.info("read index")
        file = open(os.path.join(path, 'index.txt'), 'r')
        self.index = file.readlines()
        logger.info("%d index read", len(self.index))

        logger.info("read pinying")
        file = open(os.path.join(path, 'pinying.txt'), 'r')
        self.pinyings = file.readlines()
        logger.info("%d pinying read", len(self.pinyings))

    def search(self, word):
        """Return a list of matching entries"""
        # We use bisect to optimize the speed
        # Get the matching indexes
        i = bisect.bisect(self.index, word)
        line = self.index[i]
        ii = [int(x) for x in line.split('\t')[1:]]
        ret = []
        for i in ii:
            # Get the entrie
            line = unicode(self.entries[i], 'utf-8')
            entrie = line.split('\t') # e.g : 你好\thello\thow are you ?
            ch = entrie[0]
            pinying = u""
            for c in ch:
                # We have to re-encode because the lines in the lists
                # are not encoded
                p = bisect.bisect(self.pinyings, c.encode('utf-8'))
                line = self.pinyings[p]
                pinying += line.split()[1]
            translations = entrie[1:]
            ret.append(Entrie(ch, pinying, translations))
        return ret


class DictApp(tichy.Application):

    name = 'Dict'
    category = 'general'

    def run(self, window):
        self.window = gui.Window(window, modal=True)
        frame = self.view(self.window, back_button=True)
        vbox = gui.Box(frame, axis=1)
        # The search entry
        text = tichy.Text('')
        text.view(vbox, editable=True)
        text.connect('modified', self.on_text_modified)

        # The result actions
        self.results = tichy.List()
        self.results.view(vbox)

        self.dict = Dict(self.path())

        yield tichy.Wait(frame, 'back')
        self.window.destroy()

    def on_text_modified(self, text):
        self.results.clear()
        entries = self.dict.search(str(text))
        for entrie in entries:
            self.results.append(tichy.Text(entrie.unicode()))


if __name__ == '__main__':
    dict = Dict('.')
    rets = dict.search('hello')
    for e in rets:
        print e.unicode().encode('utf-8')
