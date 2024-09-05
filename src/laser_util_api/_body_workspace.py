from jsonrpcclient import request

from ._client_interface import ApiInterface
from ._loop_workspace import LoopHandle


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

    def add_inner_unchecked(self, loop: LoopHandle):
        """ Performs an unchecked insertion of a loop into the body as an inner boundary. If the loop is positive, it
        will throw an exception.  If the loop intersects with one of the body's existing boundaries, the behavior will
        be undefined. """
        data = request("InsertLoopIntoBody", params=(self.id, loop.id))
        response = self._interface(data)
        return response.result


class BodyScratchPad:
    def __init__(self, interface: ApiInterface):
        self._interface = interface

    def create(self, loop: LoopHandle) -> BodyHandle:
        data = request("BodyCreate", params=(loop.id,))
        response = self._interface(data)
        return BodyHandle(response.result, self._interface)
