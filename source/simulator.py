from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector


class Arena(Widget):
    def bounce(self, car):
        if not car.updating:
            if not self.collide_point(car.x + 120, car.y + 120)\
                    or not self.collide_point(car.x + 120, car.y - 120)\
                    or not self.collide_point(car.x - 120, car.y + 120)\
                    or not self.collide_point(car.x - 120, car.y - 120):
                car.rotate(angle=120)


class Car(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def __init__(self, **kwargs):
        super(Car, self).__init__(**kwargs)
        self.updating = False
        self.duration = 0.15

    def move(self):
        if not self.updating:
            self.pos = Vector(*self.velocity) + self.pos

    def rotate(self, angle):
        self.flag(val=True)
        self.vector(angle=angle)
        updated_angle = self.angle - angle
        anim = Animation(angle=updated_angle, duration=self.duration)
        anim.bind(on_complete=lambda *args: self.flag(val=False))
        Clock.schedule_once(callback=lambda *args: anim.start(self), timeout=0)

    def vector(self, angle):
        vector = Vector(self.velocity).rotate(-angle)
        self.velocity = vector.x, vector.y

    def flag(self, val):
        self.updating = val

        if not val:
            self.move()


class Simulator(Screen):
    car1 = ObjectProperty(None)
    car2 = ObjectProperty(None)
    car3 = ObjectProperty(None)
    car4 = ObjectProperty(None)
    arena = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(Simulator, self).__init__(**kwargs)
        Clock.schedule_once(callback=lambda *args: self.start(car=self.car1), timeout=1)

    def start(self, car, vel=(4, 0)):
        car.center = self.center
        car.velocity = vel
        Clock.schedule_interval(callback=self.update, timeout=1/30)

    def update(self, dt):
        self.car1.move()
        self.arena.bounce(self.car1)
