from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle
from kivy.properties import NumericProperty, ListProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
import random
import math
import time


ANGLE_RANGE_WIDE = (100, 130)
ANGLE_RANGE_NARROW = (40, 80)
DURATION = 0.3


class Arena(Widget):
    def bounce(self, car):
        if not car.updating:
            lhit, rhit = self.collide(obj=car)
            if lhit or rhit:
                car.update_direction()
                Clock.schedule_once(
                    callback=lambda *args: car.rotate(angle=self.safe_angle(lhit=lhit, rhit=rhit)),
                    timeout=DURATION
                )

    def safe_angle(self, lhit, rhit):
        if lhit and rhit:
            return random.randint(*ANGLE_RANGE_WIDE) * random.choice([-1, 1])
        elif lhit:
            return -random.randint(*ANGLE_RANGE_NARROW)
        else:
            return random.randint(*ANGLE_RANGE_NARROW)

    def collide(self, obj):
        lhit = not self.collide_point(*obj.abs_left())
        rhit = not self.collide_point(*obj.abs_right())
        return lhit, rhit


class Maze(GridLayout):
    obstacles = ListProperty()

    def bounce(self, obj):
        if not obj.updating:
            lhit, rhit = self.collide(obj=obj)
            if lhit or rhit:
                obj.update_direction()
                Clock.schedule_once(
                    callback=lambda *args: obj.rotate(angle=self.safe_angle(lhit=lhit, rhit=rhit)),
                    timeout=DURATION
                )

    def safe_angle(self, lhit, rhit):
        if lhit and rhit:
            return random.randint(*ANGLE_RANGE_WIDE) * random.choice([-1, 1])
        elif lhit:
            return -random.randint(*ANGLE_RANGE_NARROW)
        else:
            return random.randint(*ANGLE_RANGE_NARROW)

    def collide(self, obj):
        for obstacle in self.obstacles:
            lhit = obstacle.collide_point(*obj.abs_left())
            rhit = obstacle.collide_point(*obj.abs_right())
            if lhit or rhit:
                return lhit, rhit
        return None, None

    def add_obstacles(self):
        with open('obstacle.txt') as f:
            lines = f.readlines()

        arr = list()
        for line in lines:
            line = line.replace('\n', '')
            arr.append(line.split(' '))

        for line in arr:
            for c in line:
                o = Obstacle()
                if c == 'x':
                    self.obstacles.append(o)
                else:
                    o.color = (1, 1, 1, 1)
                self.add_widget(o)


class Car(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    arena = ObjectProperty(None)
    maze = ObjectProperty(None)
    lwing = ObjectProperty(None)
    ring = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(Car, self).__init__(**kwargs)
        self.updating = False
        self.is_forward = True

    def forward(self):
        self.pos = Vector(*self.velocity) + self.pos

    def backward(self):
        self.pos = -Vector(*self.velocity) + self.pos

    def rotate(self, angle):
        lal, lar = self.arena.collide(self.lwing)
        ral, rar = self.arena.collide(self.rwing)
        lml, lmr = self.maze.collide(self.lwing)
        rml, rmr = self.maze.collide(self.rwing)

        if lal or lar or ral or rar or lml or lmr or rml or rmr:
            if ((lal or lar) and (ral or rar)) or ((lml or lmr) and (rml or rmr)):
                Clock.schedule_once(
                    callback=lambda *args: self.rotate(angle=abs(angle) * random.choice([-1, 1])),
                    timeout=DURATION * 3
                )
            elif lal or lar or lml or lmr:
                Clock.schedule_once(
                    callback=lambda *args: self.rotate(angle=abs(angle) * -1),
                    timeout=DURATION * 3
                )
            else:
                Clock.schedule_once(
                    callback=lambda *args: self.rotate(angle=abs(angle)),
                    timeout=DURATION * 3
                )
        else:
            self.update_flag(val=True)
            self.update_vector(angle=angle)
            self.update_direction()
            self.update_arrow(direction='left' if angle > 0 else 'right')
            updated_angle = self.angle + angle
            anim = Animation(angle=updated_angle, duration=DURATION)
            anim.bind(on_complete=lambda *args: self.update_flag(val=False))
            anim.start(widget=self)

    def reset_arrow(self):
        self.arrow = 'None'

    def update_arrow(self, direction):
        self.reset_arrow()
        self.arrow = direction

    def update_direction(self):
        self.is_forward = self.is_forward != True

    def update_vector(self, angle):
        vector = Vector(self.velocity).rotate(angle)
        self.velocity = vector.x, vector.y

    def update_flag(self, val):
        self.updating = val

    def abs_left(self):
        x, y = self.x, self.y
        cx, cy = self.center_x, self.center_y
        a = math.radians(self.angle)
        nx = ((x - cx) * math.cos(a)) - ((y - cy) * math.sin(a)) + cx
        ny = ((x - cx) * math.sin(a)) + ((y - cy) * math.cos(a)) + cy
        return nx, ny

    def abs_right(self):
        x, y = self.x, self.top
        cx, cy = self.center_x, self.center_y
        a = math.radians(self.angle)
        nx = ((x - cx) * math.cos(a)) - ((y - cy) * math.sin(a)) + cx
        ny = ((x - cx) * math.sin(a)) + ((y - cy) * math.cos(a)) + cy
        return nx, ny


class Head(Widget):
    def rotate(self):
        anim = Animation(angle=40, duration=DURATION * 2) + Animation(angle=-40, duration=DURATION * 2)
        anim.repeat = True
        anim.start(widget=self)


class LWing(Widget):
    car = ObjectProperty(None)

    def abs_left(self):
        x, y = self.x + self.width, self.y
        cx, cy = self.car.center_x, self.car.center_y
        a = math.radians(self.car.angle)
        nx = ((x - cx) * math.cos(a)) - ((y - cy) * math.sin(a)) + cx
        ny = ((x - cx) * math.sin(a)) + ((y - cy) * math.cos(a)) + cy
        return nx, ny

    def abs_right(self):
        x, y = self.x, self.y
        cx, cy = self.car.center_x, self.car.center_y
        a = math.radians(self.car.angle)
        nx = ((x - cx) * math.cos(a)) - ((y - cy) * math.sin(a)) + cx
        ny = ((x - cx) * math.sin(a)) + ((y - cy) * math.cos(a)) + cy
        return nx, ny


class RWing(Widget):
    car = ObjectProperty(None)

    def abs_left(self):
        x, y = self.x, self.top
        cx, cy = self.car.center_x, self.car.center_y
        a = math.radians(self.car.angle)
        nx = ((x - cx) * math.cos(a)) - ((y - cy) * math.sin(a)) + cx
        ny = ((x - cx) * math.sin(a)) + ((y - cy) * math.cos(a)) + cy
        return nx, ny

    def abs_right(self):
        x, y = self.x + self.width, self.top
        cx, cy = self.car.center_x, self.car.center_y
        a = math.radians(self.car.angle)
        nx = ((x - cx) * math.cos(a)) - ((y - cy) * math.sin(a)) + cx
        ny = ((x - cx) * math.sin(a)) + ((y - cy) * math.cos(a)) + cy
        return nx, ny


class Obstacle(Widget):
    color = ListProperty((0.1, 0.2, 0.3, 1))


class Simulator(Screen):
    arena = ObjectProperty(None)
    maze = ObjectProperty(None)
    car = ObjectProperty(None)
    head = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(Simulator, self).__init__(**kwargs)
        Clock.schedule_once(callback=lambda *args: self.start(), timeout=1)

    def start(self, vel=(-4, 0)):
        self.car.center = self.center
        self.car.velocity = vel
        self.car.arena = self.arena
        self.car.maze = self.maze
        self.car.lwing = self.lwing
        self.car.rwing = self.rwing
        self.lwing.car = self.car
        self.rwing.car = self.car

        self.maze.add_obstacles()
        Clock.schedule_interval(callback=self.update, timeout=1/30)
        self.head.rotate()

    def update(self, dt):
        if not self.car.updating:
            self.car.forward() if self.car.is_forward else self.car.backward()
            self.car.update_arrow(direction='forward') if self.car.is_forward else self.car.update_arrow(direction='backward')
        self.arena.bounce(self.car)
        self.maze.bounce(self.car)
