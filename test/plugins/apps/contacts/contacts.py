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

import tichy
import tichy.gui as gui
from tichy.phone import TelNumber

class Contacts(tichy.Application):
    name = 'Contacts'
    icon = 'icon.png'
    category = 'general' # So that we see the app in the launcher
    design = 'Default'
     
    def run(self, parent):
        self.window = gui.Window(parent)
        frame = self.view(self.window, back_button=True)
        
        vbox = gui.Box(frame, axis=1, expand=True)
        
        self.contacts_service = tichy.Service('Contacts')
        self.contacts = self.contacts_service.contacts
        self.contacts.actors_view(vbox)
        
        new_menu = frame.actor.new_action('New')
        new_menu.connect('activated', self.on_new)
        
        yield tichy.Wait(frame, 'back') # Wait until the quit button is clicked
        self.window.destroy()   # Don't forget to close the window
        
    def on_new(self, *args):
        contact = self.contacts_service.create()
        yield Contact(self.window, contact)

class ContactAttrItem(tichy.Item):
    """This item is used to print a contact attribute"""
    def __init__(self, name, value):
        super(ContactAttrItem, self).__init__()
        self.name = name
        self.value = value
    
    # We override item.get_text cause we want to use our own view
    # method Instead ot relying on the item name
    def get_text(self):
        return self
        
    def __str__(self):
        return self.name
        
    def view(self, parent):
        ret = gui.Box(parent, axis = 0, border = 0)
        gui.Label(ret, self.name)
        self.value.view(ret)
        return ret
        
class Contact(tichy.Application):
    design = 'Default'
    
    def run(self, window, contact):
        self.contact = contact
        self.name = "Edit %s" % contact['name']
        self.window = gui.Window(window, modal = True)
        frame = self.view(self.window, back_button=True)
        
        vbox = gui.Box(frame, axis = 1)

        self.attr_list = tichy.ActorList()
        self.update_list()
        list_view = self.attr_list.view(vbox)
        
        gui.Spring(vbox, axis = 1)
        
        add_menu = frame.actor.new_action('Add')
        add_tel_menu = add_menu.new_action('Tel')
        add_note_menu = add_menu.new_action('Note')
        
        add_note_menu.connect('activated', self.on_add, tichy.Text, 'note')
        add_tel_menu.connect('activated', self.on_add, TelNumber, 'tel')
        
        yield tichy.Wait(frame, 'back')
        self.window.destroy()
        
    def on_add(self, action, item, view, item_cls, name):
        # first we have to set up a unique name for the new attr
        i = 1
        final_name = name
        while final_name in self.contact:
            i += 1
            final_name = '%s %d' % (name, i)
        name = final_name
    
        value = item_cls("")
        self.contact[name] = value
        self.update_list()
        
        value.edit(self.window, name = name)
        
    def update_list(self):
        self.attr_list.clear()
        
        for attr, value in self.contact.items():
            actor = tichy.Actor(ContactAttrItem(attr, value))
            edit = actor.new_action('Edit')
            edit.connect('activated', self.on_edit_attr)
            delete = actor.new_action('Delete')
            delete.connect('activated', self.on_delete_attr)
            self.attr_list.append(actor)
            
    def on_edit_attr(self, action, attr, view):
        yield self.contact[attr.name].edit(view.window, name = attr.name)
        
    def on_delete_attr(self, action, attr, view):
        if attr.name == 'name':
            yield tichy.Dialog(view.window, "Error", "Can't delete name")
        else:
            self.attr_list.remove(action.actor)
            del self.contact[attr.name]
            
class SelectContactApp(tichy.Application):
    name = "Select Contact"
    enabled = False
    def run(self, window):
        self.window = gui.Window(window)
        frame = self.view(self.window)
        
        vbox = gui.Box(frame, axis = 1)
        
        for contact in tichy.Service('Contacts').contacts:
            button = gui.Button(vbox)
            contact.get_text().view(button)
            button.connect('clicked', self.on_select, contact)
        
        # Wait until the quit button is clicked
        yield tichy.Wait(self.window, 'destroyed')
        yield self.ret
    
    def on_select(self, b, contact):
        self.ret = contact
        self.window.destroy()
            
            
class SelectContactService(tichy.Service):
    service = 'SelectContact'
    def select(self, window):
        return SelectContactApp(window)
        
class EditContactService(tichy.Service):
    service = 'EditContact'
    def edit(self, contact, window):
        yield Contact(window, contact) 
