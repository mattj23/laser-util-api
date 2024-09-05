import json
from dataclasses import dataclass
from uuid import uuid4, UUID
from jsonrpcclient import request

from ._client_interface import ApiInterface
from .vector import Vector, Xyr, Units
from ._project_items import ProjectItem

from enum import IntEnum


class HAlign(IntEnum):
    LEFT = 0
    CENTER = 1
    RIGHT = 2


class VAlign(IntEnum):
    TOP = 0
    CENTER = 1
    BOTTOM = 2


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

class EtchTransaction:
    def __init__(self, project_item: ProjectItem, interface: ApiInterface):
        self._project_item = project_item
        self._interface = interface
        self._payload = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        prepared = json.dumps([x.to_dict() for x in self._payload])

        data = request("AddEtchEntityItem", params=(str(self._project_item.id), prepared,))
        response = self._interface(data)
        if not response.result:
            raise Exception("Failed to add etch item")
        return response.result


    def add_line(self, start: Vector, end: Vector, width: float):
        """
        Add a line to the etch item.
        :param start: The starting point of the line
        :param end: The ending point of the line
        :param width: The width of the line
        """
        payload = EtchLine(uuid4(),
                           self._interface.convert_to_api(start),
                           self._interface.convert_to_api(end),
                           self._interface.convert_to_api(width))
        self._payload.append(payload)

    def add_text(self, position: Vector, r: float, text: str, font_id: int,
                 vertical: VAlign = VAlign.CENTER,
                 horizontal: HAlign = HAlign.CENTER):
        """
        Add text to the etch item.
        :param position: The reference position of the text
        :param r: The rotation of the text in radians.
        :param text: The text to add to the etch item
        :param font_id: The ID of the font to use, found in the workspace settings under "Fonts"
        :param vertical: Vertical alignment
        :param horizontal: Horizontal alignment
        """
        payload = EtchText(uuid4(),
                           self._interface.convert_to_api(position),
                           r,
                           text,
                           font_id,
                           int(vertical),
                           int(horizontal))
        self._payload.append(payload)


class EtchItem(ProjectItem):

    def _add_payload(self, payload):
        working = []
        if hasattr(payload, "__iter__"):
            working.extend(payload)
        else:
            working.append(payload)

        prepared = json.dumps([x.to_dict() for x in working])

        data = request("AddEtchEntityItem", params=(self._id_str(), prepared,))
        response = self._interface(data)
        if not response.result:
            raise Exception("Failed to add etch item")
        return response.result

    def transaction(self) -> EtchTransaction:
        return EtchTransaction(self, self._interface)

    def add_line(self, start: Vector, end: Vector, width: float):
        """
        Add a line to the etch item.
        :param start: The starting point of the line
        :param end: The ending point of the line
        :param width: The width of the line
        """
        payload = EtchLine(uuid4(),
                           self._interface.convert_to_api(start),
                           self._interface.convert_to_api(end),
                           self._interface.convert_to_api(width))
        self._add_payload([payload])

    def add_text(self, position: Vector, r: float, text: str, font_id: int, vertical: VAlign, horizontal: HAlign):
        """
        Add text to the etch item.
        :param position: The reference position of the text
        :param r: The rotation of the text in radians.
        :param text: The text to add to the etch item
        :param font_id: The ID of the font to use, found in the workspace settings under "Fonts"
        :param vertical: Vertical alignment
        :param horizontal: Horizontal alignment
        """
        payload = EtchText(uuid4(),
                           self._interface.convert_to_api(position),
                           r,
                           text,
                           font_id,
                           int(vertical),
                           int(horizontal))
        self._add_payload([payload])
