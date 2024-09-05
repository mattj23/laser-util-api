import socket
import json
import time
from pathlib import Path
from typing import Union

from ._common import is_uuid, UUID
from ._etch_item import EtchItem
from ._work_settings import MaterialOption, FontOption
from .vector import Units
from ._client_interface import ApiInterface
from ._loop_workspace import LoopScratchPad, LoopHandle
from ._body_workspace import BodyHandle, BodyScratchPad
from ._item_factory import create_entity
from jsonrpcclient import request, parse, Error, Ok

from ._project_items import ProjectItem

# ==========================================================================================
# Body and Loop Scratch Workspace
# ==========================================================================================
class ScratchPad:
    def __init__(self, interface: ApiInterface):
        self.loops = LoopScratchPad(interface)
        self.bodies = BodyScratchPad(interface)

# ==========================================================================================
# High-level Project Methods
# ==========================================================================================
class ProjectCommands:
    def __init__(self, interface: ApiInterface):
        self._rpc = interface

    def name(self) -> str:
        data = request("GetProjectName")
        response = self._rpc(data)
        print(response)
        return response.result

    def path(self) -> str:
        data = request("GetProjectPath")
        response = self._rpc(data)
        return response.result

    def save_as(self, path: Union[Path, str]):
        data = request("SaveProjectAs", params=(str(path),))
        response = self._rpc(data)
        return response.result

    def new(self):
        data = request("CreateNewProject")
        response = self._rpc(data)
        return response.result

    def open(self, path: Union[Path, str]):
        if isinstance(path, Path):
            path = str(path)
        data = request("OpenProject", params=(path,))
        response = self._rpc(data)
        return response.result

# ==========================================================================================
# WorkSettings Methods
# ==========================================================================================
class WorkSettingsCommands:
    def __init__(self, interface: ApiInterface):
        self._rpc = interface

    def material_options(self) -> list[MaterialOption]:
        data = request("GetWorkSettingsMaterialOptions")
        response = self._rpc(data)
        return [MaterialOption(item, self._rpc) for item in response.result]

    def active_material(self) -> MaterialOption:
        data = request("GetWorkSettingsSelectedMaterial")
        response = self._rpc(data)
        return MaterialOption(response.result, self._rpc)

    @property
    def kerf(self) -> float:
        data = request("GetWorkSettingsKerf")
        response = self._rpc(data)
        return self._rpc.convert_from_api(response.result)

    @kerf.setter
    def kerf(self, value: float):
        data = request("SetWorkSettingsKerf", params=[self._rpc.convert_to_api(value)])
        response = self._rpc(data)
        if not response.result:
            raise Exception("Failed to set kerf")

    @property
    def kerf_override(self) -> bool:
        data = request("GetWorkSettingsKerfOverride")
        response = self._rpc(data)
        return response.result

    @kerf_override.setter
    def kerf_override(self, value: bool):
        data = request("SetWorkSettingsKerfOverride", params=[value])
        response = self._rpc(data)
        if not response.result:
            raise Exception("Failed to set kerf override")

    def fonts(self) -> list[FontOption]:
        data = request("GetWorkSettingsFonts")
        response = self._rpc(data)
        return [FontOption(item, self._rpc) for item in response.result]

    def find_font(self, id: int) -> FontOption:
        data = request("GetWorkSettingsFont", params=(id,))
        response = self._rpc(data)
        return FontOption(response.result, self._rpc)

    def create_font(self) -> FontOption:
        data = request("CreateWorkSettingsFont")
        response = self._rpc(data)
        return FontOption(response.result, self._rpc)

    def get_system_font_families(self) -> list[str]:
        data = request("GetSystemFontFamilies")
        response = self._rpc(data)
        return response.result



# ==========================================================================================
# Project Tree/Entity Methods
# ==========================================================================================
class TreeCommands:
    def __init__(self, interface: ApiInterface):
        self._rpc = interface

    def __iter__(self):
        return _TreeIterator(self._all())

    def __getitem__(self, key: Union[int, str, UUID]):
        if isinstance(key, int):
            return self._all()[key]

        if isinstance(key, UUID):
            return self._by_id(str(key))

        if isinstance(key, str):
            if is_uuid(key):
                return self._by_id(key)

            for item in self._all():
                if str(item.id).startswith(key):
                    return item

        raise ValueError("key must be an integer, UUID, or string")

    def _all(self) -> list[ProjectItem]:
        """ Get all entities in the project """
        data = request("GetEntities")
        response = self._rpc(data)
        return [create_entity(item, self._rpc) for item in response.result]

    def _by_id(self, id: str) -> ProjectItem:
        """ Find an entity by its ID """
        data = request("FindEntity", params=(id, ))
        response = self._rpc(data)
        return create_entity(response.result, self._rpc)

    def with_tag(self, tag: str) -> list[ProjectItem]:
        """ Find all entities with a specific tag """
        data = request("GetEntitiesByTag", params=(tag, ))
        response = self._rpc(data)
        return [create_entity(item, self._rpc) for item in response.result]

class _TreeIterator:
    def __init__(self, items: list[ProjectItem]):
        self._items = items
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index >= len(self._items):
            raise StopIteration
        item = self._items[self._index]
        self._index += 1
        return item

# ==========================================================================================
# Entity Creation
# ==========================================================================================
class CreationCommands:
    def __init__(self, interface: ApiInterface):
        self._rpc = interface

    def body(self, source: Union[LoopHandle, BodyHandle]) -> ProjectItem:
        if isinstance(source, LoopHandle):
            data = request("CreateBodyEntityFromLoop", params=[source.id])
        elif isinstance(source, BodyHandle):
            data = request("CreateBodyEntityFromBody", params=[source.id])
        else:
            raise ValueError("source must be a LoopHandle or BodyHandle")

        response = self._rpc(data)
        return ProjectItem(response.result, self._rpc)

    def etch(self) -> EtchItem:
        data = request("CreateEtchEntityEmpty")
        response = self._rpc(data)
        return EtchItem(response.result, self._rpc)


class ApiClient:
    def __init__(self, port: int = 5000, host: str = "localhost", units=Units.MM):
        self.port = port
        self.host = host
        self.socket = None
        self.units = units
        self._interface = ApiInterface(lambda: self.units, self._rpc)

        # Sub-interfaces
        self.scratch = ScratchPad(self._interface)
        self.project = ProjectCommands(self._interface)
        self.tree = TreeCommands(self._interface)
        self.create = CreationCommands(self._interface)
        self.work_settings = WorkSettingsCommands(self._interface)

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
        # Receive a newline-terminated JSON object from the socket with a 5-second timeout
        if self.socket is None:
            raise Exception("Socket is not connected")

        time.sleep(0.010)

        self.socket.settimeout(5)
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

