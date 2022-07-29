from dataclasses import field
from typing import Tuple, List, Literal
import tkinter as tk
from numpy import array
from numpy.linalg import norm as distance
from copy import deepcopy


class Config:
    SCREEN_SIZE: Tuple[int, int] = (900, 700)
    BACKGROUND: str = "#191E29"
    POINT_SIZE: int = 16  # In pixels
    POINT_COLOR: str = "#FFFFFF"
    LOCKED_POINT_COLOR: str = "#E6394C"
    STICK_WIDTH: int = 10
    STICK_COLOR: int = "#292E39"
    STICK_ITERATIONS: int = 10


class Point:
    def __init__(self, position: Tuple[float, float], locked=False):
        self.position: array = array([float(position[0]), float(position[1])])
        self.locked: bool = locked
        self.prevPosition: array = array([float(position[0]), float(position[1])])
        self.body: tk.Canvas.create_oval = field(repr=False, init=False)

    def __repr__(self) -> str:
        return f"<{'LOCKED ' if self.locked else ''}Point at [%d, %d]>" % (
            self.position[0],
            self.position[1],
        )


class Stick:
    def __init__(self, pointA: Point, pointB: Point, length: float):
        self.pointA: Point = pointA
        self.pointB: Point = pointB
        self.length: float = length
        self.body: tk.Canvas.create_line = field(repr=False, init=False)

    def __repr__(self) -> str:
        return f"<Stick (%.2fpx) [{self.pointA}, {self.pointB}]>" % self.length


class Screen:
    def __init__(self):
        self.points: List[Point] = []
        self.sticks: List[Stick] = []
        self.master = tk.Tk()
        self.canvas: tk.Canvas = self.init_canvas()
        self.tempPoint = None
        self.moving_point = None
        self.structures: List[List[Stick]] = []

    def init_canvas(self) -> tk.Canvas:
        canvas = tk.Canvas(
            master=self.master,
            width=Config.SCREEN_SIZE[0],
            height=Config.SCREEN_SIZE[1],
            background=Config.BACKGROUND,
        )
        canvas.pack()
        canvas.bind("<ButtonPress-1>", self.click)
        canvas.bind("<B1-Motion>", self.drag)
        canvas.bind("<ButtonRelease-1>", self.release)
        return canvas

    def create_point(self, x, y) -> None:
        self.points.append(Point(array((x, y))))

    def create_stick(self, pointA: Point, pointB: Point) -> None:
        self.sticks.append(
            Stick(
                pointA=pointA,
                pointB=pointB,
                length=distance(pointA.position - pointB.position),
            )
        )

    def click(self, event) -> None:
        position = array([event.x, event.y])
        for point in self.points:
            if distance(position - point.position) < Config.POINT_SIZE:
                self.tempPoint = point
                return

    def drag(self, event) -> None:
        position = array([event.x, event.y])
        for point in self.points:
            if distance(position - point.position) < Config.POINT_SIZE and point.locked:
                self.moving_point = point
        if self.moving_point:
            self.moving_point.position = position
            self.simulate_frame()

    def release(self, event) -> None:
        position = array([event.x, event.y])
        if self.moving_point:
            self.moving_point = None
            self.draw_screen()
            return
        for point in self.points:
            if distance(position - point.position) < Config.POINT_SIZE:
                if point is self.tempPoint:
                    point.locked = not point.locked
                    self.draw_screen()
                    return
                if self.tempPoint:
                    self.create_stick(self.tempPoint, point)
                    self.draw_screen()
                    # self.find_structures()
                return
        self.create_point(event.x, event.y)
        self.tempPoint = None
        self.draw_screen()

    def draw_points(self) -> None:
        for point in self.points:
            self.canvas.delete(point.body)
            point.body = self.canvas.create_oval(
                point.position[0] - Config.POINT_SIZE,
                point.position[1] - Config.POINT_SIZE,
                point.position[0] + Config.POINT_SIZE,
                point.position[1] + Config.POINT_SIZE,
                fill=Config.LOCKED_POINT_COLOR if point.locked else Config.POINT_COLOR,
                width=0,
            )

    def draw_sticks(self) -> None:
        for stick in self.sticks:
            self.canvas.delete(stick.body)
            stick.body = self.canvas.create_line(
                stick.pointA.position[0],
                stick.pointA.position[1],
                stick.pointB.position[0],
                stick.pointB.position[1],
                fill=Config.STICK_COLOR,
                width=Config.STICK_WIDTH,
            )

    def draw_screen(self) -> None:
        self.draw_sticks()
        self.draw_points()
        self.canvas.update()
        self.canvas.update_idletasks()

    def simulate_frame(self) -> None:
        for _ in range(Config.STICK_ITERATIONS):
            for stick in self.sticks:
                if stick.pointA.locked:
                    self.calculate_joint(stick, "B")
                elif stick.pointB.locked:
                    self.calculate_joint(stick, "A")
        self.draw_screen()

    def calculate_joint(self, stick: Stick, letter: Literal["A", "B"]) -> None:
        joint = stick.pointA if letter == "A" else stick.pointB
        if joint.locked:
            return
        prevJoint = stick.pointB if letter == "A" else stick.pointA
        direction = (joint.position - prevJoint.position) / distance(
            joint.position - prevJoint.position
        )
        joint.position = prevJoint.position + direction * stick.length
        for next_stick in [i for i in self.sticks if i is not stick]:
            if next_stick.pointA is joint:
                self.calculate_joint(next_stick, "B")
                return
            elif next_stick.pointB is joint:
                self.calculate_joint(next_stick, "A")
                return


pantalla = Screen()
pantalla.canvas.mainloop()
