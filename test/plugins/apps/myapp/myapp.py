# coding=utf8
#    Tichy
#    copyright 2008 Guillaume Chereau (charlie@openmoko.org)
#
#    This file is part of Tichy.
#
#    Tichy is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Tichy is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Tichy.  If not, see <http://www.gnu.org/licenses/>.

import tichy
import tichy.gui as gui
import tichy.item as item
from tichy.tasklet import Wait
from tichy.application import Application

class SmallApp(Application):
    name = u'Test你好'
    category = 'general'
    def run(self, parent):
        w = gui.Window(parent, modal = True)   # We run into a new modal window
        frame = self.view(w)
        
        b = gui.Button(frame)
        gui.Label(b, 'quit')    
            
        yield Wait(b, 'clicked')     # Wait until the quit button is clicked
        w.destroy()                   # Don't forget to close the window
        
class SmallApp2(Application):
    # name = 'With a Grid'
    enabled = False
    def run(self, parent):
        w = gui.Window(parent, modal = True)   # We run into a new modal window
        frame = self.view(w)
        gbox = gui.Table(frame, axis = 1)
        for i in range(10):
            b = gui.Button(gbox)
            gui.Label(b, str(i))
        b = gui.Button(gbox)
        gui.Label(b, 'quit')        
        yield Wait(b, 'clicked')     # Wait until the quit button is clicked
        w.destroy()                   # Don't forget to close the window
        
class TangoGps(Application):
    name = 'TangoGps'
    enabled = False
    def run(self, parent):
        import subprocess
        subprocess.call('tangogps')
        yield None
        
class Suspend(Application):
    name = 'Suspend'
    enabled = False
    def run(self, parent):
        import os
        # it doesn't work !
        os.system("apm -s")

        
class SmallApp4(Application):
    name = 'Test Process'
    enabled = False
    def run(self, parent):
        from tichy.object import Object
        from tichy.tasklet import Tasklet
    
        w = gui.Window(parent, modal = True)   # We run into a new modal window
        frame = self.view(w)
        vbox = gui.Box(frame, axis = 1)
        
        text = item.Text('')
        text.view(vbox)
        
        class Process(Tasklet, Object):
            def __init__(self):
                super(Process, self).__init__()
            def run(self):
                print 'run'
                self.emit('step', 'start')
                self.emit('step', 'hello')
                self.emit('step', 'bye')
                yield None
                
        
        
        process = Process()
        def on_step(p, msg):
            text.value += "%s\n" % msg
        process.connect('step', on_step)
        
        yield process

        b = gui.Button(vbox)
        gui.Label(b, 'quit')
        yield Wait(b, 'clicked')     # Wait until the quit button is clicked
        w.destroy()                   # Don't forget to close the window
        
