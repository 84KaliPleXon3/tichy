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

import os

import tichy
from tichy import gui
from tichy.gui import Vect

import logging
logger = logging.getLogger('App.Browser')

# TODO : it is a little bit mess here. Make things cleaner

class FileItem(tichy.Item):
    """Define a special item for an entry in the file list"""
    def __init__(self, browser, path, name = None):
        self.browser = browser
        self.path = path
        self.name = name or os.path.basename(self.path).decode('utf-8', 'replace')
        
    def view(self, parent):
        ret = gui.Button(parent)
        gui.Label(ret, self.name)
        def on_clicked(w):
            self.browser.select_path(self.path)
        ret.connect('clicked', on_clicked)
        return ret

class FileBrowser(tichy.Application):
    name = 'Browser'
    icon = 'icon.png'
    category = 'general' # So that we see the app in the launcher
    
    def __init__(self, *args):
        super(FileBrowser, self).__init__(*args)
        self.list = tichy.List()
        
    def run(self, parent):
        w = gui.Window(parent, modal = True)
        frame = self.view(w, back_button="Load")
        vbox = gui.Box(frame, axis = 1)
        
        list_view = self.list.view(vbox)
        
        gui.Spring(vbox, axis = 1)
        
        self.select_path(os.path.expanduser('~/'))
        
        yield tichy.Wait(frame, 'back')     # Wait until the back button is clicked
        w.destroy()                   # Don't forget to close the window

    def select_path(self, path):
        if not os.path.isdir(path):
            return
    
        self.dir = path
        self.list.clear()
        list = sorted(os.listdir(path))
        self.list.append(FileItem(self, os.path.dirname(path), '..'))
        for file in list:
            if file.startswith('.'):
                continue
            self.list.append(FileItem(self, os.path.join(path, file)))
            
            
class SelectFileBrowser(FileBrowser):
    def __init__(self, *args):
        super(SelectFileBrowser, self).__init__(*args)
        
    def run(self, parent, file_name = '', can_create = False):
        w = gui.Window(parent, modal = True)
        msg = can_create and 'Save' or 'Load'
        frame = self.view(w, title = 'Select File', back_button=msg)
        vbox = gui.Box(frame, axis = 1)
        
        self.file_name_item = tichy.Text(file_name, editable = can_create)
        self.file_name_item.view(vbox)
        
        list_view = self.list.view(vbox)
        
        gui.Spring(vbox, axis = 1)
        
        self.select_path(os.path.expanduser('~/'))
        
        yield tichy.Wait(frame, 'back')     # Wait until the quit button is clicked
        w.destroy()                   # Don't forget to close the window
        
        # Return the result
        yield os.path.join(self.dir, self.file_name_item.value)
        
    def select_path(self, path):
        if not os.path.isdir(path):
            logger.info("selecting %s", os.path.basename(path))
            self.file_name_item.value = os.path.basename(path)
            return
    
        self.dir = path
        self.list.clear()
        list = sorted(os.listdir(path))
        self.list.append(FileItem(self, os.path.dirname(path), '..'))
        for file in list:
            if file.startswith('.'):
                continue
            self.list.append(FileItem(self, os.path.join(path, file)))
        

class FileBrowserService(tichy.Service):
    service = 'FileBrowser'
    def get_save_path(self, parent, name):
        return SelectFileBrowser(parent, name, True)
    def get_load_path(self, parent):
        return SelectFileBrowser(parent, '', False)
