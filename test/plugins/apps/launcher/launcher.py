import tichy
import tichy.gui as gui


class Launcher(tichy.Application):
    """ The main application, used to start any other application
    """
    name = "Launcher"
    enabled = False
    
    design = 'Grid'
    
    def run(self, window):
        frame = self.view(window)
        
        # We populate the frame with all the applications
        self.list_view = None
        self.populate(frame)

        def run_lock(action, app, view):
            tichy.Service('ScreenLock').run(view.window)

        lock_item = frame.actor.new_action('Screen Lock')
        # the item does not really toggle back.
        # we will need a one that does 'launched' probably
        lock_item.connect('activated', run_lock)
        
        # If the design change we repopulate the frame
        # This is a little bit tricky. We use the 'changed' signal from the Service('Design') base object... 
        def on_design_changed(s, design):
            self.populate(frame)
        tichy.Service('Design').base.connect('changed', on_design_changed)

        # Wait until the quit button is clicked
        quit_item = frame.actor.new_action('Quit')
        yield tichy.tasklet.Wait(quit_item, 'activated')
        
    def populate(self, frame):
        if self.list_view:
            self.list_view.destroy()
        # View all the enabled applications
        list = tichy.ActorList()
        for app in tichy.Application.subclasses:
            if not app.name or not hasattr(app, 'category'):
                continue
            actor = app.create_actor()
            list.append(actor)
        self.list_view = list.view(frame)
