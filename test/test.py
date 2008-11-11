#    Tichy
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

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(name)-8s %(levelname)-8s %(message)s')
logger = logging.getLogger('')

import sys
sys.path.insert(0, '../')

# Import all the stuffs we need...
import tichy
import tichy.gui as gui

tichy.plugins.import_all('plugins')

style = tichy.style.Style.find_by_name("black style").create()
tichy.Service.set_default('Design', 'Default')

print "Create painter"
painter = gui.Painter((480, 640), fullscreen=False)
print "Create events loop"
loop = gui.EventsLoop()

print "Create screen"
screen = gui.Screen(loop, painter, style=style)
loop.window = screen


class Item(tichy.Item):

    def view(self, parent):
        ret = gui.Box(parent, axis=0)
        gui.Label(ret, "Hello")
        gui.Label(ret, "Hi")
        return ret


class Test(tichy.Application):

    name = "TEST"

    def run(self, window):
        box = gui.Box(window, axis=1)
        top_frame = gui.Frame(box)
        content_frame = gui.Frame(box, expand=True)
        l = tichy.List()
        for i in range(10):
            l.append(Item())
        l.view(content_frame)
        yield tichy.tasklet.Wait(self, 'destroyed')

#launcher = tichy.Application.find_by_name('Launcher')
#launcher(screen).start()

window = gui.Window(screen)
Test(window).start()


print "start loop"
loop.run()
