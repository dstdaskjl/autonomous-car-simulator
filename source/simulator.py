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


ANGLE_RANGE = (80, 130)


class Arena(Widget):
    def bounce(self, car):
        if not car.updating:
            if self.collide(car=car):
                car.rotate(angle=self.safe_angle(car))

    def safe_angle(self, car):
        rhit = not self.collide_point(*car.abs_right())
        lhit = not self.collide_point(*car.abs_left())
        angle = random.randint(*ANGLE_RANGE)

        if rhit and lhit:
            return angle * random.choice([-1, 1])
        return angle if rhit else -angle

    def collide(self, car):
        rhit = not self.collide_point(*car.abs_right())
        lhit = not self.collide_point(*car.abs_left())
        return True if rhit or lhit else False


class Maze(GridLayout):
    obstacles = ListProperty()

    def bounce(self, car):
        if not car.updating:
            if self.collide(car=car):
                car.rotate(angle=random.randint(*ANGLE_RANGE) * random.choice([-1, 1]))

    def safe_angle(self, car):
        angle = random.randint(*ANGLE_RANGE)
        for obstacle in self.obstacles:
            rhit = obstacle.collide_point(*car.abs_right())
            lhit = obstacle.collide_point(*car.abs_left())
            if rhit and lhit:
                return angle * random.choice([-1, 1])
            if rhit:
                return angle
            if lhit:
                return -angle

    def collide(self, car):
        for obstacle in self.obstacles:
            rhit = obstacle.collide_point(*car.abs_right())
            lhit = obstacle.collide_point(*car.abs_left())
            if rhit or lhit:
                return True
        return False

    def add_obstacles(self):
        with open('maze.txt') as f:
            lines = f.readlines()

        arr = list()
        for line in lines:
            line = line.replace('\n', '')
            arr.append(line.split(' '))

        for line in arr:
            for c in line:
                o = Obstacle()
                if c != 'x':
                    o.color = (1, 1, 1, 1)
                else:
                    self.obstacles.append(o)
                self.add_widget(o)


class Car(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def __init__(self, **kwargs):
        super(Car, self).__init__(**kwargs)
        self.updating = False
        self.duration = 0.3

    def forward(self):
        self.pos = Vector(*self.velocity) + self.pos
        # print(self.pos)
        # print()

    def backward(self):
        self.pos = -Vector(*self.velocity) + self.pos

    def rotate(self, angle):
        self.update_flag(val=True)
        self.update_vector(angle=angle)
        updated_angle = self.angle + angle
        anim = Animation(angle=updated_angle, duration=self.duration)
        anim.bind(on_complete=lambda *args: self.update_flag(val=False))
        Clock.schedule_once(callback=lambda *args: anim.start(self), timeout=0)

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


class Obstacle(Widget):
    color = ListProperty((0.1, 0.2, 0.3, 1))


class Simulator(Screen):
    car = ObjectProperty(None)
    arena = ObjectProperty(None)
    maze = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(Simulator, self).__init__(**kwargs)
        Clock.schedule_once(callback=lambda *args: self.start(car=self.car, maze=self.maze), timeout=1)

    def start(self, car, maze, vel=(-8, 0)):
        car.center = self.center
        car.velocity = vel
        maze.add_obstacles()
        Clock.schedule_interval(callback=self.update, timeout=1/30)

    def update(self, dt):
        if not self.car.updating:
            self.car.forward()
        self.arena.bounce(self.car)
        self.maze.bounce(self.car)
