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

    def __mul__(self, other: Union[float, Transform]) -> Vector:
        if isinstance(other, float):
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

    # def transform_array(self, vectors: numpy.ndarray) -> numpy.ndarray:
    #     assert vectors.shape[1] == 3
    #     padded = numpy.hstack((vectors, numpy.ones((vectors.shape[0], 1))))
    #     return numpy.array(self.matrix.dot(padded.T).T[:, :3])

    # @staticmethod
    # def from_basis_vectors(x0: Vector, y0: Vector, origin: Vector) -> Transform:
    #     # x0 is the main basis vector and the only one which is completely unmodified
    #     x = x0.unit()
    #
    #     # y0 must be projected onto x0 and then normalized to ensure it is orthogonal
    #     y = (y0 - x * x.dot(y0)).unit()
    #
    #     z = x.cross(y).unit()
    #     t = numpy.eye(4)
    #     t[:3, 0] = x.to_array()
    #     t[:3, 1] = y.to_array()
    #     t[:3, 2] = z.to_array()
    #     t[:3, 3] = origin.to_array()
    #     return Transform(t).invert()
    #
    # @staticmethod
    # def from_isometry(d: Dict) -> Transform:
    #     """ Create a transform from an isometry dictionary that came out of nalgebra """
    #     i, j, k, w = d["rotation"]
    #     x, y, z = d["translation"]
    #
    #     # First row of the rotation matrix
    #     r00 = 2 * (w * w + i * i) - 1
    #     r01 = 2 * (i * j - w * k)
    #     r02 = 2 * (i * k + w * j)
    #
    #     # Second row of the rotation matrix
    #     r10 = 2 * (i * j + w * k)
    #     r11 = 2 * (w * w + j * j) - 1
    #     r12 = 2 * (j * k - w * i)
    #
    #     # Third row of the rotation matrix
    #     r20 = 2 * (i * k - w * j)
    #     r21 = 2 * (j * k + w * i)
    #     r22 = 2 * (w * w + k * k) - 1
    #
    #     matrix = numpy.array([[r00, r01, r02, x],
    #                           [r10, r11, r12, y],
    #                           [r20, r21, r22, z],
    #                           [0, 0, 0, 1]])
    #     return Transform(matrix)
    #
    @staticmethod
    def identity() -> Transform:
        return Transform(numpy.eye(3))

    # @staticmethod
    # def from_euler(order: str, angles: List[float]):
    #     matrix = numpy.eye(4)
    #     matrix[:3, :3] = Rotation.from_euler(order, angles).as_matrix()
    #     return Transform(matrix)
    #
    # @staticmethod
    # def from_flat(flat: List[float]):
    #     return Transform(numpy.matrix(flat).reshape(4, 4))
    #
    # def to_flat(self):
    #     return list(self.matrix.flat)
    #
    # def rotation_only(self) -> Transform:
    #     new_matrix = numpy.eye(4)
    #     new_matrix[:3, :3] = self.matrix[:3, :3]
    #     return Transform(new_matrix)
    #
    # @staticmethod
    # def rotate_around_axis(theta, axis_vector):
    #     from math import cos, sin
    #     u = axis_vector.unit()
    #     m = [
    #         [cos(theta) + u.x ** 2 * (1 - cos(theta)), u.x * u.y * (1 - cos(theta)) - u.z * sin(theta),
    #          u.x * u.z * (1 - cos(theta)) + u.y * sin(theta), 0],
    #         [u.y * u.x * (1 - cos(theta)) + u.z * sin(theta), cos(theta) + u.y ** 2 * (1 - cos(theta)),
    #          u.y * u.z * (1 - cos(theta)) - u.x * sin(theta), 0],
    #         [u.z * u.x * (1 - cos(theta)) - u.y * sin(theta), u.z * u.y * (1 - cos(theta)) + u.x * sin(theta),
    #          cos(theta) + u.z ** 2 * (1 - cos(theta)), 0],
    #         [0, 0, 0, 1]
    #     ]
    #     return Transform(numpy.matrix(m))
    #

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

    # def serialize(self):
    #     """
    #     Serialize the transformation into a json encoded dictionary
    #     """
    #     return json.dumps(list(list(r) for r in self.matrix))
    #
    # def save(self, path):
    #     with open(path, "w") as handle:
    #         handle.write(self.serialize())
    #
    # @staticmethod
    # def deserialize(text):
    #     m = json.loads(text)
    #     return Transform(numpy.matrix(m))
    #
    # @staticmethod
    # def load(path):
    #     with open(path, "r") as handle:
    #         return Transform.deserialize(handle.read())
