
import e_dbus
import evas
import evas.decorators
import edje
import edje.decorators
import ecore
import ecore.evas
import etk

import tichy

def Vect(x,y):
    return (x,y)
    
def Rect(pos, size):
    return (pos, size)

class Widget(tichy.Object):
    def __init__(self, parent, etk_obj = None, item = None, expand = False, **kargs):
        self.etk_obj = etk_obj or etk.VBox()
        self.item = item
        self.parent = parent
        self.children = []
        self.expand = expand
        if self.parent:
            self.parent.get_contents_child().add(self)
        self.show()
    def add(self, child):
        self.etk_obj.add(child.etk_obj)
        self.children.append(child)
    def get_evas(self):
        return self.parent.get_evas()
    def show(self):
        self.etk_obj.show_all()
        
    def get_contents_child(self):
        return self
        
    def parent_as(self, cls):
        if isinstance(self.parent, cls):
            return self.parent
        return self.parent.parent_as(cls)
        
    def __get_window(self):
        return self.parent_as(Window)
    window = property(__get_window)
    
    def destroy(self):
        self.etk_obj.destroy()
        
    # No tags for this implementation
    def add_tag(self, tag):
        pass
    def remove_tag(self, tag):
        pass
        
class Window(Widget):
    def __init__(self, parent, **kargs):
        etk_obj = etk.Window(w=480, h=640)
        Widget.__init__(self, None, etk_obj=etk_obj)
    def show(self):
        self.etk_obj.show()
        super(Window, self).show()

        
class Screen(Window):
    def __init__(self, loop, painter, **kargs):
        super(Screen, self).__init__(None)

class Box(Widget):
    def __init__(self, parent, axis=0, **kargs):
        if axis == 0:
            etk_obj = etk.HBox()
        else:
            etk_obj = etk.VBox()
        super(Box, self).__init__(parent, etk_obj=etk_obj, **kargs)
        
    def add(self, child):
        policy = etk.VBox.FILL
        if child.expand:
            policy = etk.VBox.EXPAND_FILL
        self.etk_obj.append(child.etk_obj, etk.VBox.START, policy, 0)
        
class Frame(Box):
    def __init__(self, parent, **kargs):
        # self.etk_obj = Canvas()
        # edje_obj = edje.Edje(parent.get_evas(), file='test.edj', group="frame")
        # self.etk_obj.object_add(edje_obj)
        super(Frame, self).__init__(parent, **kargs)
        # edje_obj.show()
        
class Fixed(Widget):
    pass
        
class Table(Widget):
    pass
    
class Table(Widget):
    def __init__(self, parent, nb = 3, **kargs):
        self.nb = nb
        self.current = 0
        etk_obj = etk.Table(nb, 5, etk.Table.HOMOGENEOUS)
        super(Table, self).__init__(parent, etk_obj=etk_obj, **kargs)
    def add(self, child):
        x = self.current % self.nb
        y = self.current / self.nb
        self.etk_obj.attach_default(child.etk_obj, x, x, y, y)
        self.current += 1

class Scrollable(Widget):
    def __init__(self, parent, **kargs):
        etk_obj = etk.ScrolledView()
        super(Scrollable, self).__init__(parent, etk_obj=etk_obj, **kargs)
    def add(self, child):
        self.etk_obj.add_with_viewport(child.etk_obj)
        
class Button(Widget):
    def __init__(self, parent, **kargs):
        etk_obj = etk.Button()
        super(Button, self).__init__(parent, etk_obj=etk_obj, **kargs)
        self.etk_obj.connect('clicked', self.on_clicked)
    def on_clicked(self, *args):
        self.emit('clicked')
    
class Label(Widget):
    def __init__(self, parent, text, **kargs):
        etk_obj = etk.Label(text)
        super(Label, self).__init__(parent, etk_obj=etk_obj, **kargs)
        
    def __get_text(self):
        return self.etk_obj.get()
    def __set_text(self, value):
        self.etk_obj.set(value)
    text = property(__get_text, __set_text)
    
class Edit(Widget):
    def __init__(self, parent, item = None, **kargs):
        etk_obj = etk.Entry()
        super(Edit, self).__init__(parent, etk_obj=etk_obj, **kargs)
        
    
class Spring(Widget):
    def __init__(self, parent, expandable = True, **kargs):
        super(Spring, self).__init__(parent, expandable=expandable, **kargs)
        
        
class SurfWidget(Widget):
    pass
    
class ImageWidget(Widget):
    def __init__(self, parent, image, **kargs):
        self.image = image
        etk_obj = etk.Image()
        etk_obj.set_from_file(image.path)
        super(ImageWidget, self).__init__(parent, etk_obj=etk_obj, **kargs)
        
        
        
class ScrollableSlide(Widget):
    pass
    
    
class Painter(object):
    def __init__(self, size, fullscreen = None):
        pass
        
        
class EventsLoop(object):
    def run(self):
        ecore.main_loop_begin()
        
    def timeout_add(self, time, callback, *args):
        return ecore.timer_add(time / 1000, callback, *args) 
