from typing import Callable
from jsonrpcclient import request, Ok

from laser_api._client_interface import ApiInterface


class LoopHandle:
    def __init__(self, guid: str, interface: ApiInterface):
        self.id = guid
        self._interface = interface
