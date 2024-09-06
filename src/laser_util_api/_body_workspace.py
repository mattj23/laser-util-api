from jsonrpcclient import request

from ._client_interface import ApiInterface
from ._loop_workspace import LoopHandle
from .vector import Aabb, Vector, Xyr


class BodyHandle:
    def __init__(self, guid: str, interface: ApiInterface):
        self.id = guid
        self._interface = interface

    def operate(self, loop: LoopHandle):
        """ Perform an operations on the body with the specified loop as the tool. If the loop is positive, it will
        perform an add (union) operation.  If the loop is negative, it will perform a cut (intersection) operation. """
        data = request("BodyOperate", params=(self.id, loop.id))
        response = self._interface(data)
        return response.result

    def operate_copies(self, loop: LoopHandle, transforms: list[Xyr]):
        """ Perform a set of operations on the body with the specified loop as a tool, in which the tool is copied and
         transformed once for each transform in the list before the operation is done. This allows bulk generation of
         pattern based features. """
        t = [{"X": x.x, "Y": x.y, "R": x.r} for x in map(self._interface.convert_to_api, transforms)]
        data = request("BodyOperateCopies", params=(self.id, loop.id, t))
        response = self._interface(data)
        return response.result

    def add_inner_unchecked(self, loop: LoopHandle):
        """ Performs an unchecked insertion of a loop into the body as an inner boundary. If the loop is positive, it
        will throw an exception.  If the loop intersects with one of the body's existing boundaries, the behavior will
        be undefined. """
        data = request("InsertLoopIntoBody", params=(self.id, loop.id))
        response = self._interface(data)
        return response.result

    @property
    def bounds(self) -> Aabb:
        data = request("GetBodyBounds", params=(self.id, ))
        response = self._interface(data)
        b_min = Vector(response.result["MinX"], response.result["MinY"])
        b_max = Vector(response.result["MaxX"], response.result["MaxY"])
        return Aabb(self._interface.convert_from_api(b_min), self._interface.convert_from_api(b_max))

class BodyScratchPad:
    def __init__(self, interface: ApiInterface):
        self._interface = interface

    def create(self, loop: LoopHandle) -> BodyHandle:
        data = request("BodyCreate", params=(loop.id,))
        response = self._interface(data)
        return BodyHandle(response.result, self._interface)
