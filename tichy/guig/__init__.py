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

# This file contains an implementation of the gui widget using gtk as
# a backend It is still very experimental, and many things are
# missing.  I need to clean the code of gui to make this
# implementation as simple as possible It has to be simple cause I
# want to allow several other backends : etk, clutter, Qt, etc...

import pygtk
pygtk.require('2.0')
import gtk
import gobject

import tichy

# We don't really care about the Vect and Rect class here.  We just
# use tuple instead...


def Vect(x, y):
    return (x, y)


def Rect(pos, size):
    return (pos, size)


class Widget(tichy.Object):

    def __init__(self, parent, expand=False, item=None, pos=None,
                 optimal_size=None, min_size=None,
                 gtk_obj=None, **kargs):
        super(Widget, self).__init__()
        self.parent = parent
        self.children = []
        self.expand = expand
        self.pos = pos or Vect(0, 0)
        self.item = item
        self.gtk_obj = gtk_obj or gtk.VBox()

        if min_size:
            self.gtk_obj.set_size_request(min_size[0], min_size[1])
        # Hack to avoid bug :
        # http://bugzilla.gnome.org/show_bug.cgi?id=546802 (to remove
        # when the bug is fixed)
        self.gtk_obj.__dict__
        if self.parent:
            self.parent.get_contents_child().add(self)
        self.gtk_obj.show()

    def get_contents_child(self):
        return self

    def parent_as(self, cls):
        if isinstance(self.parent, cls):
            return self.parent
        return self.parent.parent_as(cls)

    def __get_window(self):
        return self.parent_as(Window)
    window = property(__get_window)

    def add(self, child):
        self.gtk_obj.add(child.gtk_obj)
        self.children.append(child)

    def on_clicked(self, gtk_obj):

        self.emit('clicked')

    def destroy(self):
        self.gtk_obj.destroy()

    def add_tag(self, tag):
        pass

    def remove_tag(self, tag):
        pass


class Screen(Widget):

    def __init__(self, loop, painter, **kargs):
        gtk_obj = gtk.Window(gtk.WINDOW_TOPLEVEL)
        super(Screen, self).__init__(None, gtk_obj=gtk_obj)


class Box(Widget):

    def __init__(self, parent, axis=1, **kargs):
        if axis == 0:
            gtk_obj = gtk.HBox()
        else:
            gtk_obj = gtk.VBox()
        super(Box, self).__init__(parent, gtk_obj=gtk_obj, **kargs)

    def add(self, child):
        self.gtk_obj.pack_start(child.gtk_obj, expand=child.expand,
                                fill=True, padding=0)
        self.children.append(child)


class Window(Widget):

    def __init__(self, parent, **kargs):
        gtk_obj = gtk.Window(gtk.WINDOW_TOPLEVEL)
        super(Window, self).__init__(None, gtk_obj=gtk_obj, **kargs)
        self.gtk_obj.maximize()

    def close(self):
        self.gtk_obj.destroy()


class Frame(Box):

    pass


class SurfWidget(Frame):

    pass


class Table(Widget):

    def __init__(self, parent, nb=3, **kargs):
        self.nb = nb
        self.current = 0
        gtk_obj = gtk.Table(nb, 5)
        super(Table, self).__init__(parent, gtk_obj=gtk_obj, **kargs)

    def add(self, child):
        x = self.current % self.nb
        y = self.current / self.nb
        self.gtk_obj.attach(child.gtk_obj, x, x+1, y, y+1)
        self.current += 1


class Fixed(Widget):

    def __init__(self, parent, **kargs):
        gtk_obj = gtk.Fixed()
        super(Fixed, self).__init__(parent, gtk_obj=gtk_obj, **kargs)

    def add(self, child):
        self.gtk_obj.put(child.gtk_obj, child.pos[0], child.pos[1])


class ImageWidget(Widget):

    def __init__(self, parent, image, **kargs):
        self.image = image
        gtk_obj = gtk.Image()
        gtk_obj.set_from_file(image.path)
        super(ImageWidget, self).__init__(parent, gtk_obj=gtk_obj, **kargs)


class Spring(Widget):

    def __init__(self, parent, axis=1, expand=True, **kargs):
        gtk_obj = gtk.VBox()   # TODO : use something better than that
        super(Spring, self).__init__(parent, expand=expand,
                                     gtk_obj=gtk_obj, **kargs)


class Label(Widget):

    def __init__(self, parent, text, **kargs):
        gtk_obj = gtk.Label(text)
        super(Label, self).__init__(parent, gtk_obj=gtk_obj, **kargs)

    def __get_text(self):
        return self.gtk_obj.get_text()

    def __set_text(self, value):
        self.gtk_obj.set_text(value)

    text = property(__get_text, __set_text)


class Edit(Widget):

    def __init__(self, parent, item=None, **kargs):
        text = str(item)
        gtk_obj=gtk.Entry()
        gtk_obj.set_text(str(item))
        super(Edit, self).__init__(parent, gtk_obj=gtk_obj, **kargs)


class ScrollableSlide(Frame):

    pass


class Button(Widget):

    def __init__(self, parent, **kargs):
        gtk_obj = gtk.Button()

        def on_clicked(gtk, self):
            self.on_clicked(gtk)
        gtk_obj.connect('clicked', on_clicked, self)

        super(Button, self).__init__(parent, gtk_obj=gtk_obj, **kargs)


class Scrollable(Widget):

    def __init__(self, parent, axis=1, **kargs):
        gtk_obj = gtk.ScrolledWindow()
        super(Scrollable, self).__init__(parent, gtk_obj=gtk_obj, **kargs)

    def add(self, child):
        self.gtk_obj.add_with_viewport(child.gtk_obj)


class Painter(object):

    def __init__(self, size, fullscreen=None):
        pass


class EventsLoop(object):

    def __init__(self):
        import gobject
        self.gobject_loop = gobject.MainLoop()

    def run(self):
        self.gobject_loop.run()

    def quit(self):
        self.gobject_loop.quit()

    def timeout_add(self, time, callback, *args):
        return gobject.timeout_add(time, callback, *args)

    def __get_dbus_loop(self):
        import dbus
        return dbus.mainloop.glib.DBusGMainLoop()

    dbus_loop = property(__get_dbus_loop)
