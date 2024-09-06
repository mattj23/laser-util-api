from __future__ import annotations

from enum import Enum

import numpy
from dataclasses import dataclass
from typing import Union


class Units(Enum):
    INCHES = 1
    MM = 2

    def to_mm(self, value):
        if self == Units.INCHES:
            return value * 25.4
        else:
            return value

    def from_mm(self, value):
        if self == Units.INCHES:
            return value / 25.4
        else:
            return value

    def suffix(self):
        return "mm" if self == Units.MM else "in"


@dataclass
class Xyr:
    x: float
    y: float
    r: float

    @staticmethod
    def from_dict(d: dict) -> Xyr:
        return Xyr(d["X"], d["Y"], d["R"])

    @staticmethod
    def identity() -> Xyr:
        return Xyr(0, 0, 0)


@dataclass
class Vector:
    x: float
    y: float

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __neg__(self):
        return Vector(-self.x, -self.y)

    def __mul__(self, other: Union[float, Transform, int]) -> Vector:
        if isinstance(other, float):
            return Vector(self.x * other, self.y * other)
        if isinstance(other, int):
            return Vector(self.x * other, self.y * other)
        elif isinstance(other, Transform):
            moved = other * numpy.array([self.x, self.y, 1])
            return Vector(moved[0], moved[1])
        else:
            raise TypeError("Can only multiply by scalar or a transform")

    def __truediv__(self, other: float) -> Vector:
        return Vector(self.x / other, self.y / other)

    def norm(self):
        return numpy.sqrt(self.x ** 2 + self.y ** 2)

    def unit(self):
        return self / self.norm()

    def dot(self, other: Vector):
        return self.x * other.x + self.y * other.y

    def signed_angle(self, other: Vector) -> float:
        return numpy.atan2(self.x * other.y - self.y * other.x, self.x * other.x + self.y * other.y)

    def cross(self, other):
        # Cross product of b x c (this vector is b)
        return self.x * other.y - self.y * other.x

    def angle_to(self, other: Vector) -> float:
        return numpy.arccos(self.dot(other) / (self.norm() * other.norm()))

    def to_array(self) -> numpy.ndarray:
        return numpy.array([self.x, self.y])

    def __list__(self):
        return [self.x, self.y]

    def __getitem__(self, item):
        return [self.x, self.y][item]

    def __iter__(self):
        yield self.x
        yield self.y


ORIGIN = Vector(0, 0)
AXIS_X = Vector(1.0, 0)
AXIS_Y = Vector(0, 1.0)


class Transform:
    def __init__(self, matrix: Union[numpy.matrix, numpy.ndarray]):
        self.matrix = matrix if isinstance(matrix, numpy.matrix) else numpy.matrix(matrix)

    def __mul__(self, other: Union[numpy.matrix, Transform, Vector]):
        if isinstance(other, numpy.matrix):
            return Transform(self.matrix @ other)
        elif isinstance(other, Transform):
            return Transform(self.matrix @ other.matrix)
        elif isinstance(other, Vector):
            moved = self.matrix @ numpy.array([other.x, other.y, 1])
            if moved.shape == (1, 4):
                return Vector(moved[0, 0], moved[0, 1])
            return Vector(moved[0], moved[1])
        else:
            raise TypeError("Can only multiply by numpy matrix, Vector, or Transform")

    def __str__(self):
        return numpy.array_str(self.matrix, suppress_small=True, precision=6)

    def to_xyr(self) -> Xyr:
        return Xyr(self.matrix[0, 2], self.matrix[1, 2], numpy.arctan2(self.matrix[1, 0], self.matrix[0, 0]))

    @staticmethod
    def from_xyr(xyr: Xyr) -> Transform:
        return Transform(numpy.array([[numpy.cos(xyr.r), -numpy.sin(xyr.r), xyr.x],
                                      [numpy.sin(xyr.r), numpy.cos(xyr.r), xyr.y],
                                      [0, 0, 1]]))

    @staticmethod
    def identity() -> Transform:
        return Transform(numpy.eye(3))

    @staticmethod
    def rotate(theta: float):
        return Transform(numpy.array([[numpy.cos(theta), -numpy.sin(theta), 0],
                                      [numpy.sin(theta), numpy.cos(theta), 0],
                                      [0, 0, 1]]))

    @staticmethod
    def translate(*args):
        if len(args) == 2:
            return Transform._translate(*args)
        elif len(args) == 1:
            arg = args[0]
            if hasattr(arg, "x") and hasattr(arg, "y"):
                return Transform.translate(arg.x, arg.y)
        raise TypeError(f"Could not create translation from {args}")

    @staticmethod
    def _translate(x, y):
        m = numpy.eye(3)
        m[0, 2] = x
        m[1, 2] = y
        return Transform(m)

    def invert(self) -> Transform:
        return Transform(numpy.linalg.inv(self.matrix))


class Aabb:
    def __init__(self, min_bound: Vector, max_bound: Vector):
        self.min_bound = min_bound
        self.max_bound = max_bound
        self.__corners = None

    @property
    def center(self) -> Vector:
        return (self.max_bound + self.min_bound) * 0.5

    @property
    def extent(self) -> Vector:
        return self.max_bound - self.min_bound

    @property
    def corners(self) -> list[Vector]:
        if self.__corners is None:
            self.__corners = [
                Vector(self.min_bound.x, self.min_bound.y),
                Vector(self.min_bound.x, self.max_bound.y),
                Vector(self.max_bound.x, self.max_bound.y),
                Vector(self.max_bound.x, self.min_bound.y),
            ]
        return self.__corners

    def merged_with(self, other: Aabb) -> Aabb:
        return Aabb(Vector(min(self.min_bound.x, other.min_bound.x), min(self.min_bound.y, other.min_bound.y)),
                    Vector(max(self.max_bound.x, other.max_bound.x), max(self.max_bound.y, other.max_bound.y)))

    def __intersects_aabb(self, box: Aabb) -> bool:
        if self.max_bound.x < box.min_bound.x or self.min_bound.x > box.max_bound.x:
            return False

        if self.max_bound.y < box.min_bound.y or self.min_bound.y > box.max_bound.y:
            return False

        return True

    def __intersects_vector(self, v: Vector) -> bool:
        return (self.min_bound.x <= v.x <= self.max_bound.x and
                self.min_bound.y <= v.y <= self.max_bound.y)

    def intersects(self, geom: Union[Aabb, Vector]) -> bool:
        if isinstance(geom, Aabb):
            return self.__intersects_aabb(geom)
        elif isinstance(geom, Vector):
            return self.__intersects_vector(geom)

        raise NotImplemented(f"No intersection method for type {type(geom)}")

    def closest_point(self, geom: Union[Vector]) -> Vector:
        if isinstance(geom, Vector):
            cx = max(min(geom.x, self.max_bound.x), self.min_bound.x)
            cy = max(min(geom.y, self.max_bound.y), self.min_bound.y)
            return Vector(cx, cy)

        raise NotImplemented(f"No closest point method for type {type(geom)}")

    def closest_distance(self, geom: Union[Vector]) -> float:
        p = self.closest_point(geom)
        return (p - geom).norm()

    def farthest_distance(self, geom: Union[Vector]) -> float:
        p = self.farthest_point(geom)
        return (p - geom).norm()

    def farthest_point(self, geom: Union[Vector]) -> Vector:
        if isinstance(geom, Vector):
            return max(self.corners, key=lambda v: v.distance_to(geom))

        raise NotImplemented(f"No closest point method for type {type(geom)}")

    @staticmethod
    def from_points(points: list[Vector]) -> Aabb:
        xs = [p.x for p in points]
        ys = [p.y for p in points]
        return Aabb(Vector(min(xs), min(ys)), Vector(max(xs), max(ys)))
