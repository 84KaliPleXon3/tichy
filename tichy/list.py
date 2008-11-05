
from .item import Item
from .service import Service

class List(list, Item):
    def __init__(self, values = []):
        list.__init__(self, values)
        Item.__init__(self)
        assert hasattr(self, '_Object__listeners'), self
        
    def clear(self):
        self[:] = []
        self.emit('cleared')
        self.emit('modified')
        
    def append(self, value):
        list.append(self, value)
        self.emit('appened', value)
        self.emit('modified')
        
    def remove(self, value):
        list.remove(self, value)
        self.emit('removed', value)
        self.emit('modified')
        
    def view(self, parent, **kargs):
        design = Service('Design')
        return design.view_list(parent, self, **kargs)
            
    def actors_view(self, parent, can_delete = True):
        """Return a view that contains actors view to all the elements of this list
        
           arguments:
             can_delete - if true we add a "Delete" action to every elements of the list
        """
        # This methid is tricky. Modify with care
        actors = ActorList()
        
        # Called when the user want to delete an item
        def on_delete(action, item, view):
            actors.remove(action.actor)
            self.remove(item)
        
        # Called when the original list is modified
        def on_modified(l):
            actors.clear()
            for e in self:
                actor = e.create_actor()
                if can_delete:
                    actor.new_action("Delete").connect('activated', on_delete)
                actors.append(actor)
        
        connection = self.connect('modified', on_modified)
        on_modified(self)
        view = actors.view(parent)
        
        # This is super important because otherwise the connection is never deleted
        def on_destroyed(view, connection):
            self.disconnect(connection)
        
        view.connect('destroyed', on_destroyed, connection)
        
        return view
        
        
class ActorList(List):
    def view(self, parent, **kargs):
        design = Service('Design')
        return design.view_actor_list(parent, self, **kargs)
        
