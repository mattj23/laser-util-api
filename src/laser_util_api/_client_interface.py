from typing import Callable, Union
from jsonrpcclient import Ok
from .vector import Vector, Transform, Xyr, Units


class ApiInterface:
    def __init__(self, get_units: Callable[[], Units], rpc_call: Callable[[dict], Ok]):
        self.get_units = get_units
        self._rpc = rpc_call

    def __call__(self, *args, **kwargs):
        return self._rpc(*args, **kwargs)

    def convert_from_api(self, value: Union[float, Vector, Xyr]):
        u = self.get_units()
        if isinstance(value, Vector):
            return Vector(u.from_mm(value.x), u.from_mm(value.y))
        elif isinstance(value, Xyr):
            return Xyr(u.from_mm(value.x), u.from_mm(value.y), value.r)
        else:
            return u.from_mm(value)

    def convert_to_api(self, value: Union[float, Vector, Xyr]):
        u = self.get_units()
        if isinstance(value, Vector):
            return Vector(u.to_mm(value.x), u.to_mm(value.y))
        elif isinstance(value, Xyr):
            return Xyr(u.to_mm(value.x), u.to_mm(value.y), value.r)
        else:
            return u.to_mm(value)



