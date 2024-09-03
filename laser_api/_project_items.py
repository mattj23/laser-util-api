from __future__ import annotations
from typing import Optional, Union

from jsonrpcclient import request, Ok
from uuid import UUID

from ._client_interface import ApiInterface
from .vector import Xyr


class ProjectItem:
    def __init__(self, values: dict, interface: ApiInterface):
        self.type_name = values["TypeName"].replace("ViewModel", "")
        self.id = UUID(values["Info"]["Id"])
        self._interface = interface

        self._name = values["Info"]["Name"]

        self._origin_id = values["Info"]["Origin"]["Id"]
        self._origin_parent = UUID(values["Info"]["Origin"]["ParentId"])
        self._origin = self._interface.convert_from_api(Xyr.from_dict(values["Info"]["Origin"]["Xyr"]))

    def _id_str(self) -> str:
        return str(self.id)

    def __repr__(self):
        return f"[{self.type_name} ({str(self.id)[:8]}) {self._name}]"

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        data = request("SetEntityName", params=[self._id_str(), value])
        response = self._interface(data)
        if not response.result:
            raise Exception("Failed to set entity name")
        self._name = value


    @property
    def origin(self) -> Xyr:
        return self._origin

    @origin.setter
    def origin(self, value: Xyr):
        t = self._interface.convert_to_api(value)
        data = request("SetEntityOrigin", params=[self._id_str(), t.x, t.y, t.r])
        response = self._interface(data)
        if not response.result:
            raise Exception("Failed to set entity origin")
        self._origin = value

    @property
    def origin_id(self) -> int:
        return self._origin_id

    @property
    def origin_parent(self) -> Optional[UUID]:
        if self._origin_parent == UUID("00000000-0000-0000-0000-000000000000"):
            return None
        return self._origin_parent

    @origin_parent.setter
    def origin_parent(self, value: Union[ProjectItem, UUID, None]):
        if value is None:
            value = UUID("00000000-0000-0000-0000-000000000000")
        elif isinstance(value, ProjectItem):
            value = value.id

        data = request("SetEntityOriginParent", params=[self._id_str(), str(value)])
        response = self._interface(data)
        if not response.result:
            raise Exception("Failed to set entity origin parent")
        self._origin_parent = value

    def delete(self):
        data = request("DeleteEntity", params=[self._id_str()])
        response = self._interface(data)
        if not response.result:
            raise Exception("Failed to delete entity")


