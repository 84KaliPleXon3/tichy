#    Tichy
#    copyright 2008 Michael "Goodwill" (openmoko /a/ webhippo.org)
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

version = "0.1"

import logging
logger = logging.getLogger('App.MainMenu')

import os
import shlex

## tichy imports ##
import tichy
from tichy import gui
from tichy.gui import Vect


## xdg imports ##
try:
    import xdg.Menu
    import xdg.IconTheme
except ImportError:
    logger.info("Failed to import pyxdg modules")

def shlex_split(s):
  return map(lambda x: unicode(x, "UTF-8"),
      shlex.split(s.encode("UTF-8")))

# from http://effbot.org/librarybook/os.htm
# this is a temp solution to complete 0.1 version
def spawn(program, *args):
    try:
        return os.spawnvp(os.P_NOWAIT, program, (program,) )
    except AttributeError:
        pass


class XdgMenuItem(tichy.Item):
    def __init__(self, main_app, entry):
        self.main_app = main_app
        self.entry = entry
        self.name = 'unknown'
        self.button = None

    def get_icon_path(self):
        # TODO: xdg has cached icons, maybe we can use those instead
        # other wise I think there will be a slow down
        # TODO: resize image to 96x96??
        icon_name = self.entry.getIcon()
        icon_path = xdg.IconTheme.getIconPath(iconname=icon_name,
                                              size=32,
                                              theme=self.main_app.xdg_theme)

        # (extension param does not seem to work well??)
        if icon_path is None or \
           not os.path.exists(icon_path) or \
           not icon_path[-3:] in ('png','svg','xpm','gif'):

            icon_path = xdg.IconTheme.getIconPath(iconname='image-missing',
                                                  size=32,
                                                  theme='gnome',
                                                  extensions=['png'])
        return icon_path

    def view(self, parent):
        ### should I use actor?
        displayButton = gui.Button(parent)
        displayButtonBox = gui.Box(displayButton, axis = 0)
        tichy.Image(self.get_icon_path(),
                  size = Vect(96,96)).view(displayButtonBox)
        tichy.Text(self.name).view(displayButtonBox)

        self.button = displayButton
        self.button.connect('clicked', self.on_click)
        return self.button


class XdgMenuEntry(XdgMenuItem):
    """Define a launcher item for an entry in the xdg list"""
    def __init__(self, main_app, entry):
        super(XdgMenuEntry, self).__init__(main_app, entry)
        self.name = entry.getName()

    def on_click(self, window):
        self.run_app()

    # taken from rox-xdg-menu and perverted ;)
    def run_app(self, *args):
        path = None
        cmdv = None
        entry_type = self.entry.getType()
        if entry_type == "Application":
            e = self.get_exec_expanded()
            if e:
                cmdv = shlex_split(e)
                if self.entry.getTerminal():
                    cmdv[0:0] = shlex_split(self.terminal) + ["-e"]
                path = self.entry.getPath()
            logger.info("Lauching: %s", " ".join(cmdv))
            spawn(cmdv[0], *cmdv[1:])


    def get_exec_expanded(self):
        e = self.entry.getExec()
        if e is None: return None
        icon = self.entry.getIcon()
        cmd = ""
        i, n = 0, len(e)
        while i < n:
            c = e[i]; i += 1
            if c != "%":
                cmd += c
            else:
                c = e[i]; i = i+1
                if c == "%":
                    cmd += c
                elif c == "i" and icon:
                    cmd += "--icon \"%s\"" % icon
                elif c == "c":
                    cmd += "\"%s\"" % self.entry.getName()
        return cmd


class XdgMenu(XdgMenuItem):
    """Define a sub menu entry of the xdg app list"""
    def __init__(self, main_app, entry, name=None):
        super(XdgMenu, self).__init__(main_app, entry)
        self.name = name or entry.getName() + ' >>'

    def on_click(self, window):
        self.main_app.generate_xdg_menu(self.entry)

class MainMenu(tichy.Application):
    name = 'Main Menu'
    icon = 'icon.png'
    # category = 'general' # So that we see the app in the launcher

    def __init__(self, *args):
        super(MainMenu, self).__init__(*args)
        self.list = tichy.List()
        self.current_xdg_menu = None

        #### icon theme ####
        self.xdg_theme = 'gnome'
        logger.info("Using icon theme: %s" % (self.xdg_theme,))
        #### supported desktopentry types ####
        self.xdg_types = ('Application',)
        logger.info("Limit to following .desktop types: %s" %
                     (self.xdg_types,))

    def run(self, parent):
        #### build and layout ####
        mainWindow = gui.Window(parent, modal = True)
        appFrame = self.view(mainWindow, back_button=True)
        vbox = gui.Box(appFrame, axis = 1, border=0)
        appListView = self.list.view(vbox)
        gui.Spring(vbox, axis = 1)
        upButton = gui.Button(vbox)
        gui.Label(upButton,'.. previous menu ..')

        upButton.connect('clicked',self.go_up)

        #### retrieve app list ####
        self.generate_xdg_menu(xdg.Menu.parse())

        #### close button ####
        yield tichy.Wait(appFrame,'back')
        mainWindow.destroy()

    def go_up(self, window):
       if isinstance(self.current_xdg_menu.Parent, xdg.Menu.Menu):
          self.generate_xdg_menu(self.current_xdg_menu.Parent)

    def generate_xdg_menu(self, xdg_menu):
        self.list.clear()
        self.current_xdg_menu = xdg_menu
        for entry in xdg_menu.getEntries():
            if isinstance(entry, xdg.Menu.Menu):
                if entry.getName() == '.hidden': continue
                self.list.append(XdgMenu(self, entry))
            elif isinstance(entry, xdg.Menu.MenuEntry):
                if entry.DesktopEntry.getType() in self.xdg_types:
                    self.list.append(XdgMenuEntry(self, entry.DesktopEntry))



