from __future__ import annotations

import json

from .vector import Vector, Transform
from dataclasses import dataclass
from uuid import uuid4, UUID
from enum import Enum


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


@dataclass
class EtchLine:
    id: UUID
    start: Vector
    end: Vector
    width: float

    def to_dict(self, units: Units):
        return {
            "$type": "line",
            "id": str(self.id),
            "x0": units.to_mm(self.start.x),
            "y0": units.to_mm(self.start.y),
            "x1": units.to_mm(self.end.x),
            "y1": units.to_mm(self.end.y),
            "width": units.to_mm(self.width)
        }


@dataclass
class EtchText:
    id: UUID
    position: Vector
    r: float
    text: str
    font_id: int
    vertical: int
    horizontal: int

    def to_dict(self, units: Units):
        return {
            "$type": "text",
            "id": str(self.id),
            "x": units.to_mm(self.position.x),
            "y": units.to_mm(self.position.y),
            "r": units.to_mm(self.r),
            "text": self.text,
            "fontId": self.font_id,
            "vertical": self.vertical,
            "horizontal": self.horizontal
        }


class EtchElements:
    def __init__(self, units: Units = Units.INCHES):
        self.elements = []
        self.units = units

    def add(self, element):
        self.elements.append(element)

    def add_line(self, start: Vector, end: Vector, width: float):
        self.elements.append(EtchLine(uuid4(), start, end, width))

    def add_text(self, position: Vector, r: float, text: str, font_id: int, vertical: int, horizontal: int):
        self.elements.append(EtchText(uuid4(), position, r, text, font_id, vertical, horizontal))

    def write(self, file_obj):
        json.dump([element.to_dict(self.units) for element in self.elements], file_obj, indent=2)
