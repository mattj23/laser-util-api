from jsonrpcclient import request, Ok

from laser_api import Vector
from laser_api._client_interface import ApiInterface


class LoopHandle:
    def __init__(self, guid: str, interface: ApiInterface):
        self.id = guid
        self._interface = interface

    def move_cursor_to(self, i: int):
        data = request("LoopMoveCursorTo", params=(self.id, i))
        response = self._interface(data)
        return response.result

    def reverse(self):
        data = request("LoopReverse", params=self.id)
        response = self._interface(data)
        return response.result

    def insert_arc_abs(self, point: Vector, center: Vector, is_cw: bool):
        p = self._interface.convert_to_api(point)
        c = self._interface.convert_to_api(center)
        data = request("LoopInsertArcAbs", params=(self.id, p.x, p.y, c.x, c.y, is_cw))
        response = self._interface(data)
        return response.result

    def insert_arc_rel(self, point: Vector, center: Vector, is_cw: bool):
        p = self._interface.convert_to_api(point)
        c = self._interface.convert_to_api(center)
        data = request("LoopInsertArcRel", params=(self.id, p.x, p.y, c.x, c.y, is_cw))
        response = self._interface(data)
        return response.result

    def insert_seg_abs(self, point: Vector) -> int:
        p = self._interface.convert_to_api(point)
        data = request("LoopInsertSegAbs", params=(self.id, p.x, p.y))
        response = self._interface(data)
        return response.result

    def insert_seg_rel(self, point: Vector) -> int:
        p = self._interface.convert_to_api(point)
        data = request("LoopInsertSegRel", params=(self.id, p.x, p.y))
        response = self._interface(data)
        return response.result


class LoopScratchPad:
    def __init__(self, interface: ApiInterface):
        self._interface = interface

    def create(self) -> LoopHandle:
        data = request("LoopCreate")
        response = self._interface(data)
        return LoopHandle(response.result, self._interface)


    def circle(self, center: Vector, radius: float) -> LoopHandle:
        c = self._interface.convert_to_api(center)
        r = self._interface.convert_to_api(radius)

        data = request("LoopCircle", params=(c.x, c.y, r))
        response = self._interface(data)
        return LoopHandle(response.result, self._interface)


    def rectangle(self, corner: Vector, width: float, height: float) -> LoopHandle:
        c = self._interface.convert_to_api(corner)
        w = self._interface.convert_to_api(width)
        h = self._interface.convert_to_api(height)

        data = request("LoopRectangle", params=(c.x, c.y, w, h))
        response = self._interface(data)
        return LoopHandle(response.result, self._interface)


    def rounded_rectangle(self, corner: Vector, width: float, height: float, radius: float) -> LoopHandle:
        c = self._interface.convert_to_api(corner)
        w = self._interface.convert_to_api(width)
        h = self._interface.convert_to_api(height)
        r = self._interface.convert_to_api(radius)

        data = request("LoopRoundedRectangle", params=(c.x, c.y, w, h, r))
        response = self._interface(data)
        return LoopHandle(response.result, self._interface)

    def clear(self):
        data = request("LoopsClearAll")
        response = self._interface(data)
        return response.result
