from laser_api import Vector, ApiClient, Units


def main():
    client = ApiClient(units=Units.INCHES)
    etch = client.create_etch()
    etch.name = "RPC Created Etch"


    pocket_corner = Vector(0.75, -0.775)
    first_tooth_x = 0.2
    tooth_pitch = 0.1
    tooth_height = 0.153 + 0.018
    printable_height = 0.27
    font_size = 12
    font_height = 1 / 72.0 * font_size
    font_scale = 1.2

    # Vector from the bottom to the top of the printable area
    d = Vector(0, -printable_height)
    dn = d.unit()

    # The spacing between a pocket and its diagonal neighbor
    pocket_spacing = Vector(8.0, -14.355 / 9.0)

    for row in range(10):
        for col in range(2):
            corner = pocket_corner + Vector(pocket_spacing.x * col, pocket_spacing.y * row)

            for i in [1, 6, 12, 18, 24, 30, 36, 42, 48, 54, 60, 66, 72]:
                # Point at the bottom of the printable area, located at the top of the tooth
                bottom = corner + Vector(first_tooth_x + tooth_pitch * (i - 1), -tooth_height)

                # Point at the top of the lower line
                lower_end = bottom + dn * (printable_height * 0.5 - font_scale * font_height / 2)

                # Point at the bottom of the upper line
                upper_end = bottom + dn * (printable_height * 0.5 + font_scale * font_height / 2)

                # Point at the center of the text
                center = bottom + dn * printable_height * 0.5

                # Point at the top of the printable area
                top = bottom + d

                etch.add_line(bottom, lower_end, 0.01)
                etch.add_text(center, 0, f"{i}", 1, 1, 1)
                etch.add_line(top, upper_end, 0.01)


if __name__ == "__main__":
    main()