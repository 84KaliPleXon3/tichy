
from .item import Item
from .service import Service

class Text(Item):
    def __init__(self, value, editable = False):
        super(Text, self).__init__()
        self.__value = unicode(value)
        self.editable = editable
    
    def get_text(self):
        return self
        
    def __get_value(self): return self.__value
    def __set_value(self, v) :
        self.__value = v
        self.emit('modified')
        
    value = property(__get_value, __set_value)
    
    def input_method(self):
        return None
    
    def __str__(self):
        return self.__value
        
    def __len__(self):
        return len(self.__value)
    
    def __getitem__(self, index):
        return self.__value[index]
    
    def __cmp__(self, o):
        return cmp(self.__value, unicode(o))
    
    def view(self, parent, editable = None, **kargs):
        from .gui import Label, Edit
        editable = editable if editable is not None else self.editable
        if not editable:
            ret = Label(parent, self.__value, **kargs)
        else:
            ret = Edit(parent, item = self, **kargs)
            
        connection = self.connect('modified', Text.on_modified, ret)
        ret.connect('destroyed', self.on_view_destroyed, connection)
        return ret

    def edit(self, window, **kargs):
        # first we get the appropriate TextEdit Service
        text_edit = Service('TextEdit')
        # Then we call the service with our text
        return text_edit.edit(window, self, input_method = self.input_method(), **kargs)
        
    def on_modified(self, view):
        view.text = self.__value
        
    def on_view_destroyed(self, view, connection):
        self.disconnect(connection)
        
    def create_actor(self):
        from actor import Actor
        ret = Actor(self)
        def on_edit(actor, item, view):
            yield item.edit(view.window)
        ret.new_action("Edit").connect('activated', on_edit)
        return ret
        
