
import tichy
from tichy import gui
from tichy.gui import Vect

class ActionBar(gui.Widget):
    def __init__(self, parent):
        super(ActionBar, self).__init__(parent)
        scrollable = gui.Scrollable(self, axis=0)
        self.box = gui.Box(scrollable, axis=0, border=0, spacing=0)
        self.buttons = []
        
    def clear(self):
        for b in self.buttons:
            b.destroy()
            
    def set_actor(self, actor, view):
        self.clear()
        for a in actor.actions:
            b = gui.Button(self.box)
            gui.Label(b, a.name)
            def on_clicked(b, a):
                a.activate(b)
            b.connect('clicked', on_clicked, a)
            self.buttons.append(b)
            
class ApplicationFrame(gui.Frame):
    icon = None
    class Bar(gui.Frame):
        def __init__(self, parent, app, back_button = False, **kargs):
            self.app = app
            super(ApplicationFrame.Bar, self).__init__(
                parent, min_size = Vect(0, 96), 
                tags = ['application-bar'],  # So that the style knows how to deal with this
                **kargs
            )
            box = gui.Box(self, axis = 0)
            app.actor.view(box, expand=True)
            if back_button:
                msg = "back" if back_button is True else back_button 
                back = gui.Button(
                    box, min_size=Vect(0,0), tags = ['back-button']
                )
                gui.Label(back, msg)
                back.connect('clicked', self.on_back)
        def on_back(self, b):
            self.app.emit('back')
            
    class Content(gui.Frame):
        def __init__(self, parent):
            super(ApplicationFrame.Content, self).__init__(parent, min_size=Vect(480, 0), border=0, expand=True)
            
    def get_text(self):
        return tichy.Text(self.title)
        
    def path(self, file_name = None):
        return self.app.path(file_name)
         
    def __init__(self, parent, app, title = None, border = 0, back_button = False, expand=True, **kargs):
        assert isinstance(app, tichy.Application), app
        self.app = app
        
        super(ApplicationFrame, self).__init__(parent, border=0, expand=expand, **kargs)
        self.title = title or app.name
        self.icon = app.icon
        self.content = self
        self.box = gui.Box(self, axis=1, border=0, spacing=0, expand=True)
        # self.bar = ApplicationFrame.Bar(self.box, title = title)
        self.actor = tichy.Actor(self)
        
        self.bar = ApplicationFrame.Bar(self.box, self, back_button=back_button)
        self.content = ApplicationFrame.Content(self.box)
        
        self.action_bar = ActionBar(self.box)

        self.menu_view = None

        
    def get_contents_child(self):
        return self.content

