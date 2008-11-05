
from math import sin, cos, pi

import tichy
from tichy import gui
from tichy.gui import Vect

from tichy.tasklet import Tasklet, WaitFirst, Wait

class ActorView(gui.Button):
    """An actor view with the icon above the name"""
    def __init__(self, parent, actor, **kargs):
        assert isinstance(actor, tichy.Actor)
        super(ActorView, self).__init__(parent, item=actor, tags=['grid-item'])
        box = gui.Box(self, axis=1, spacing=0, border=0)
        icon_frame = gui.Frame(box, border=0)
        if actor.item.icon:
            icon_path = actor.item.path(actor.item.icon)
            icon = tichy.Image(icon_path, size=Vect(96,96)).view(icon_frame)
        else:
            gui.Widget(icon_frame, min_size=Vect(96,96))
        actor.get_text().view(box)

class GridDesign(tichy.Service):
    enabled = True
    service = 'Design'
    name = 'Grid'
    
    def view_actor_list(self, parent, actors, **kargs):
        ret = gui.Frame(parent, item=actors, expand=True, **kargs)
        scroll = gui.Scrollable(ret, item=actors, axis=1, expand = True)
        box = gui.Table(scroll, axis=1, border=0)
        for actor in actors:
            view = ActorView(box, actor)
            def on_clicked(b, actor):
                # This method is defined in the default design
                # It will put the actors action in the application frame
                self.select_actor(actor, b)
            view.connect('clicked', on_clicked, actor)
        return ret
        
        
    def __getattr__(self, name):
        # This is a hack to use the Default Design service methods if the methid is not defined
        # I which I could instead declare the class like : class WheelDesign(Service("Default"))
        return getattr(tichy.Service('Design', 'Default'), name)
