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
        self._tags = values["Info"]["Tags"]

        self._origin_id = values["Info"]["Origin"]["Id"]
        self._origin_parent = UUID(values["Info"]["Origin"]["ParentId"])
        self._origin = self._interface.convert_from_api(Xyr.from_dict(values["Info"]["Origin"]["Xyr"]))
        self._visible = values["Info"]["IsVisible"]
        self._suppressed = values["Info"]["IsSuppressed"]
        self._drag_locked = values["Info"]["IsLocked"]

    def _id_str(self) -> str:
        return str(self.id)

    def __repr__(self):
        return f"[{self.type_name} ({str(self.id)[:8]}) {self._name}]"

    @property
    def visible(self) -> bool:
        return self._visible

    @visible.setter
    def visible(self, value: bool):
        data = request("SetEntityVisibility", params=[self._id_str(), value])
        response = self._interface(data)
        if not response.result:
            raise Exception("Failed to set entity visible")
        self._visible = value

    @property
    def drag_locked(self) -> bool:
        return self._drag_locked

    @drag_locked.setter
    def drag_locked(self, value: bool):
        data = request("SetEntityLocked", params=[self._id_str(), value])
        response = self._interface(data)
        if not response.result:
            raise Exception("Failed to set entity locked")
        self._drag_locked = value

    @property
    def for_construction(self) -> bool:
        return self._suppressed

    @for_construction.setter
    def for_construction(self, value: bool):
        data = request("SetEntityForConstruction", params=[self._id_str(), value])
        response = self._interface(data)
        if not response.result:
            raise Exception("Failed to set entity suppressed")
        self._suppressed = value

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
    def tags(self):
        return tuple(self._tags)

    def add_tag(self, tag: str):
        data = request("AddTagToEntity", params=[self._id_str(), tag])
        response = self._interface(data)
        if not response.result:
            raise Exception("Failed to add tag")
        self._tags.append(tag)

    def remove_tag(self, tag: str):
        data = request("RemoveTagFromEntity", params=[self._id_str(), tag])
        response = self._interface(data)
        if not response.result:
            raise Exception("Failed to remove tag")
        self._tags.remove(tag)

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


