import math

from laser_api import Vector
from laser_api.client import ApiClient
from laser_api.vector import Xyr


def main():
    client = ApiClient()
    project_name = client.project_name()
    print(f"Project name: {project_name}")

    # loop = client.loop_circle(Vector(1, 2), 3)
    # print(loop)

    items = client.project_items()

    circle = next(item for item in items if item.type_name.startswith("Circle"))
    rectangle = next(item for item in items if item.type_name.startswith("Rectangle"))

    print(f"Circle: {circle.name}")
    print(f"Rectangle: {rectangle.name}")

    if circle.origin_parent is None:
        circle.origin_parent = rectangle
        circle.origin = Xyr.identity()
    else:
        circle.origin_parent = None
        circle.origin = Xyr(5, 5, math.pi / 2)

    client.close()


if __name__ == '__main__':
    main()