import socket
import json
from typing import Union

from ._etch_item import EtchItem
from .vector import Units
from ._client_interface import ApiInterface
from ._loop_workspace import LoopScratchPad, LoopHandle
from ._body_workspace import BodyHandle, BodyScratchPad
from ._item_factory import create_entity
from jsonrpcclient import request, parse, Error, Ok

from ._project_items import ProjectItem


class ScratchPad:
    def __init__(self, interface: ApiInterface):
        self.loops = LoopScratchPad(interface)
        self.bodies = BodyScratchPad(interface)


class ApiClient:
    def __init__(self, port: int = 5000, host: str = "localhost", units=Units.MM):
        self.port = port
        self.host = host
        self.socket = None
        self.units = units
        self._interface = ApiInterface(lambda: self.units, self._rpc)
        self.scratch = ScratchPad(self._interface)

    def close(self):
        if self.socket is not None:
            self.socket.close()
            self.socket = None

    def _connect(self):
        if self.socket is None:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print("Connected to server")

    def _rpc(self, request_data: dict):
        self._connect()
        payload = json.dumps(request_data) + "\n"
        self.socket.sendall(payload.encode("utf-8"))
        response = self._receive()
        return response

    def _receive(self):
        # Receive a newline-terminated JSON object from the socket with a 1-second timeout
        if self.socket is None:
            raise Exception("Socket is not connected")

        self.socket.settimeout(1)
        response = b""
        while True:
            try:
                data = self.socket.recv(1024)
                if not data:
                    break
                response += data
                if b"\n" in data:
                    break
            except socket.timeout:
                break

        payload = json.loads(response.decode("utf-8"))
        result = parse(payload)
        if isinstance(result, Error):
            raise Exception(result.message)
        return result

    # ==========================================================================================
    # High-level Project Methods
    # ==========================================================================================

    def project_name(self) -> str:
        data = request("GetProjectName")
        response = self._rpc(data)
        print(response)
        return response.result

    def project_path(self) -> str:
        data = request("GetProjectPath")
        response = self._rpc(data)
        return response.result

    # ==========================================================================================
    # Project Tree/Entity Methods
    # ==========================================================================================

    def project_items(self) -> list[ProjectItem]:
        data = request("GetEntities")
        response = self._rpc(data)
        return [create_entity(item, self._interface) for item in response.result]

    # ==========================================================================================
    # Body Entity Creation
    # ==========================================================================================

    def create_body(self, source: Union[LoopHandle, BodyHandle]) -> ProjectItem:
        if isinstance(source, LoopHandle):
            data = request("CreateBodyEntityFromLoop", params=[source.id])
        elif isinstance(source, BodyHandle):
            data = request("CreateBodyEntityFromBody", params=[source.id])
        else:
            raise ValueError("source must be a LoopHandle or BodyHandle")

        response = self._rpc(data)
        return ProjectItem(response.result, self._interface)

    # ==========================================================================================
    # Etch Entity Creation
    # ==========================================================================================

    def create_etch(self) -> EtchItem:
        data = request("CreateEtchEntityEmpty")
        response = self._rpc(data)
        return EtchItem(response.result, self._interface)

