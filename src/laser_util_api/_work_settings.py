from jsonrpcclient import request, parse, Error, Ok
from ._client_interface import ApiInterface

class MaterialOption:
    def __init__(self, values: dict, interface: ApiInterface):
        self._category = values["Category"]
        self._material = values["Material"]
        self._thickness = values["ThicknessMm"]
        self._rpc = interface
        self._kerf = values["KerfMm"]
        self._key = values["Key"]

    @property
    def category(self) -> str:
        return self._category

    @property
    def material(self) -> str:
        return self._material

    @property
    def thickness(self) -> float:
        return self._rpc.get_units().from_mm(self._thickness)

    @property
    def kerf(self) -> float:
        return self._rpc.get_units().from_mm(self._kerf)

    def __repr__(self):
        suffix = self._rpc.get_units().suffix()
        return f"[{self.category}, {self._material}, {self._thickness:0.3}{suffix}]"

    def set_active(self):
        data = request("SetWorkSettingsSelectedMaterial", params=(self._key,))
        response = self._rpc(data)
        return response.result


class FontOption:
    def __init__(self, values: dict, interface: ApiInterface):
        self._id: int = values["Id"]
        self._family: str = values["Family"]
        self._size: float = values["Size"]
        self._rpc = interface

    @property
    def id(self) -> int:
        return self._id

    def __repr__(self):
        return f"[Font ID={self.id} {self._family}, {self._size}]"

    @property
    def family(self) -> str:
        return self._family

    @family.setter
    def family(self, value: str):
        data = request("SetWorkSettingsFontFamily", params=(self.id, value))
        response = self._rpc(data)

    @property
    def size(self) -> float:
        return self._size

    @size.setter
    def size(self, value: float):
        data = request("SetWorkSettingsFontSize", params=(self.id, value))
        response = self._rpc(data)

    def delete(self):
        data = request("RemoveWorkSettingsFont", params=(self.id,))
        response = self._rpc(data)