import json
from dataclasses import dataclass
from uuid import uuid4, UUID
from jsonrpcclient import request

from .vector import Vector, Xyr, Units
from ._project_items import ProjectItem

@dataclass
class EtchLine:
    id: UUID
    start: Vector
    end: Vector
    width: float

    def to_dict(self):
        return {
            "$type": "line",
            "id": str(self.id),
            "x0": self.start.x,
            "y0": self.start.y,
            "x1": self.end.x,
            "y1": self.end.y,
            "width": self.width
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

    def to_dict(self):
        return {
            "$type": "text",
            "id": str(self.id),
            "x": self.position.x,
            "y": self.position.y,
            "r": self.r,
            "text": self.text,
            "fontId": self.font_id,
            "vertical": self.vertical,
            "horizontal": self.horizontal
        }


class EtchItem(ProjectItem):

    def _add_payload(self, payload):
        working = []
        if hasattr(payload, "__iter__"):
            working.extend(payload)
        else:
            working.append(payload)

        prepared = json.dumps([x.to_dict() for x in working])

        data = request("AddEtchEntityItem", params=(self._id_str(), prepared, ))
        response = self._interface(data)
        if not response.result:
            raise Exception("Failed to add etch item")
        return response.result

    def add_line(self, start: Vector, end: Vector, width: float):
        payload = EtchLine(uuid4(),
                           self._interface.convert_to_api(start),
                            self._interface.convert_to_api(end),
                            self._interface.convert_to_api(width))
        self._add_payload([payload])

    def add_text(self, position: Vector, r: float, text: str, font_id: int, vertical: int, horizontal: int):
        payload = EtchText(uuid4(),
                           self._interface.convert_to_api(position),
                           r,
                           text,
                           font_id,
                           vertical,
                           horizontal)
        self._add_payload([payload])
