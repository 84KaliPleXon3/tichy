from math import sin, cos, pi

import tichy
from tichy.service import Service
from tichy import gui
from tichy.gui import Vect

from tichy.tasklet import Tasklet, WaitFirst, Wait


class Wheel(gui.Widget):

    def __init__(self, parent, actors, **args):
        super(Wheel, self).__init__(parent, min_size=Vect(480, 480))
        box = gui.Fixed(self, min_size=Vect(480, 480))
        self.wheel = tichy.Image(WheelDesign.path('wheel.png'),
                                 Vect(480, 288)).view(box)
        self.actors = []
        for i, actor in enumerate(actors):
            label = actor.get_text().view(box)
            self.actors.append(label)
        self.radius = 200
        self.center = Vect(self.radius, 0)
        self.angle = pi

    def __get_angle(self):
        return self.__angle

    def __set_angle(self, value):
        self.__angle = value
        r = self.radius
        for i, actor in enumerate(self.actors):
            angle = value + i * pi / 5
            actor.pos = Vect(int(r * cos(angle)),
                             -int(r * sin(angle))) + self.center

    angle = property(__get_angle, __set_angle)

    def mouse_down(self, pos):
        self.click_pos = pos
        self.click_angle = self.angle
        task = Tasklet(self.motion_task(pos))
        task.start()
        return True

    def motion_task(self, pos):
        while True:
            e, args = yield WaitFirst(Wait(self, 'mouse-up'),
                                      Wait(self, 'mouse-motion'))
            if e == 0:
                break
            pos = args[0]
            # we need to compute the angle between the original click
            # pos and the new pos But in fact I am too lazy so I will
            # use an approximation TODO: make it faster by using a
            # step value
            self.angle = (self.click_angle + \
                              (pos - self.click_pos).x / float(self.radius))


class WheelDesign(Service):
    """Stupid design that shows a wheel

    It is not even beautiful, but can be used to understand the design
    service.
    """

    enabled = True
    service = 'Design'
    name = 'Wheel'

    def view_actor_list(self, parent, actors, **kargs):
        return Wheel(parent, actors, min_size=Vect(480, 480))

    def __getattr__(self, name):
        # This is a hack to use the Default Design service methods if
        # the methid is not defined I which I could instead declare
        # the class like : class WheelDesign(Service("Default"))
        return getattr(Service('Design', 'Default'), name)
