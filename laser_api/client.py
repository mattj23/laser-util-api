import socket
import json
import time

from . import Vector, Units
from ._client_interface import ApiInterface
from .loop_ops import LoopHandle
from jsonrpcclient import request, parse, Error, Ok

from .project_items import ProjectItem


class ApiClient:
    def __init__(self, port: int = 5000, host: str = "localhost", units = Units.INCHES):
        self.port = port
        self.host = host
        self.socket = None
        self.units = units

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

    @property
    def _interface(self) -> ApiInterface:
        return ApiInterface(lambda: self.units, self._rpc)

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
        return [ProjectItem(item, self._interface) for item in response.result]

    # ==========================================================================================
    # Loop Operations/Methods
    # ==========================================================================================

    def loop_create(self) -> LoopHandle:
        data = request("LoopCreate")
        response = self._rpc(data)
        return LoopHandle(response.result, self._interface)

    def loop_circle(self, center: Vector, radius: float) -> LoopHandle:
        data = request("LoopCircle", params=(center.x, center.y, radius))
        response = self._rpc(data)
        return LoopHandle(response.result, self._interface)