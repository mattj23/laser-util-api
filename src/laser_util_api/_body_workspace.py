from jsonrpcclient import request

from ._client_interface import ApiInterface
from ._loop_workspace import LoopHandle


class BodyHandle:
    def __init__(self, guid: str, interface: ApiInterface):
        self.id = guid
        self._interface = interface

    def operate(self, loop: LoopHandle):
        data = request("BodyOperate", params=(self.id, loop.id))
        response = self._interface(data)
        return response.result


class BodyScratchPad:
    def __init__(self, interface: ApiInterface):
        self._interface = interface

    def create(self, loop: LoopHandle) -> BodyHandle:
        data = request("BodyCreate", params=(loop.id,))
        response = self._interface(data)
        return BodyHandle(response.result, self._interface)
