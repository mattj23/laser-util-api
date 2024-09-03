from ._client_interface import ApiInterface
from ._project_items import ProjectItem
from ._etch_item import EtchItem

def create_entity(values: dict, interface: ApiInterface) -> ProjectItem:
    type_name = values["TypeName"].replace("ViewModel", "")

    if type_name == "Etch":
        return EtchItem(values, interface)
    else:
        return ProjectItem(values, interface)

