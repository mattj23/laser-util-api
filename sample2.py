import math

from laser_api import Vector, Units, Xyr, ApiClient


def main():
    client = ApiClient(units=Units.INCHES)
    loop = client.scratch.loops.create()
    loop.insert_seg_abs(Vector(0, 0))
    loop.insert_arc_rel(Vector(1, 0), Vector(1, 1), False)
    loop.insert_seg_abs(Vector(1, 2))
    loop.insert_seg_abs(Vector(0, 2))

    body = client.scratch.bodies.create(loop)

    cut0 = client.scratch.loops.rectangle(Vector(1, 0.5), 5, 1)
    cut0.reverse()
    body.operate(cut0)

    cut1 = client.scratch.loops.circle(Vector(0.375, 0.375), 0.125)
    cut1.reverse()
    body.operate(cut1)

    body_entity = client.create_body(body)
    body_entity.name = "RPC Created Body"


def main2():
    client = ApiClient(units=Units.INCHES)
    loop = client.scratch.loops.create()
    loop.insert_seg_abs(Vector(0, 0))
    loop.insert_arc_rel(Vector(1, 0), Vector(1, 1), False)
    loop.insert_seg_abs(Vector(1, 2))
    loop.insert_seg_abs(Vector(0, 2))

    body = client.create_body(loop)
    body.name = "RPC Created Loop"


def main1():
    client = ApiClient(units=Units.INCHES)

    project_name = client.project_name()
    print(f"Project name: {project_name}")

    # loop = client.loop_circle(Vector(1, 2), 3)
    # print(loop)


    items = client.project_items()
    if items:
        for item in items:
            print(f"Item: {item.name}")
            item.delete()
    else:
        loop = client.scratch.loops.rectangle(Vector(5, 5), 10, 3)
        body = client.create_body(loop)
        body.name = "RPC Created Rectangle"
        body.origin = Xyr(1, 2, 0)

# circle = next(item for item in items if item.type_name.startswith("Circle"))
    # rectangle = next(item for item in items if item.type_name.startswith("Rectangle"))
    #
    # print(f"Circle: {circle.name}")
    # print(f"Rectangle: {rectangle.name}")
    #
    # if circle.origin_parent is None:
    #     circle.origin_parent = rectangle
    #     circle.origin = Xyr.identity()
    # else:
    #     circle.origin_parent = None
    #     circle.origin = Xyr(5, 5, math.pi / 2)
    #
    # client.close()


if __name__ == '__main__':
    main()