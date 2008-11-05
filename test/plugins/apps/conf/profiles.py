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

class ProfileItem(tichy.Item):
    def __init__(self, name):
        self.name = name
        

class ProfilesConf(tichy.Application):
    name = 'Profiles'
     
    def run(self, parent):
        self.window = gui.Window(parent)
        frame = self.view(self.window, back_button=True)
        
        vbox = gui.Box(frame, axis=1, expand=True)
        
        self.prefs = tichy.Service('Prefs')
        
        self.current_text = tichy.Text("current : %s" % self.prefs.get_profile())
        self.current_text.view(vbox)
        
        # We create the list of all the profiles
        profiles_list = tichy.ActorList()
        for profile in self.prefs.get_profiles():
            profile_item = ProfileItem(profile)
            actor = tichy.Actor(profile_item)
            set_action = actor.new_action('Use')
            set_action.connect('activated', self.on_set_profile)
            profiles_list.append(actor)
        
        profiles_list.view(vbox)
        
        yield tichy.Wait(frame, 'back')     # Wait until the back button is clicked
        self.window.destroy()                   # Don't forget to close the window
        
    def on_set_profile(self, action, profile, window):
        print "set profile to", profile.name
        self.prefs.set_profile(profile.name)
        self.current_text.value = "current : %s" % profile.name

