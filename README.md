# Python API for Laser Utility

This is a public Python API for the *Laser Utility* program.

When running, *Laser Utility* hosts a local JSON-RPC over TCP server bound to a local port on the loopback address.  This API provides a series of constructs which allow you to work with the internal state of the software with a native feel in Python.  Internally, the various API objects are maintaining state in order to provide the appearance of a shared application domain, while instead transforming actions into discrete JSON-RPC calls.

## Installation

Install the `laser-util-api` package from PyPi.  For example, using `pip`:

```bash
pip install laser-util-api
```

## General Connection and Client Settings
To connect to the API, the *Laser Utility* program must be running.  In the lower left corner of the software, the RPC server port will be displayed next to a green circle.  The default port is 5000, but concurrent open windows will take the next available port in ascending order.

If no arguments are supplied, the client will default to port 5000 and length units of millimeters.

```python
from laser_util_api import ApiClient

client = ApiClient()
```

Alternatively, port and units can be specified.

```python
from laser_util_api import ApiClient, Units

client = ApiClient(port=5001, units=Units.INCHES)
```

## Project-Level Functions

Project level functions allow things like saving, loading, and creating new projects, and finding the project name and path.

Saving a project:

```python 
from laser_util_api import ApiClient
from pathlib import Path

save_dir = Path("D:\\temp\\laser")

client = ApiClient()

# This will add the correct extension if the path does not end with it already
client.project.save_as(save_dir / "test")
```

Loading a project.  *Be warned, the API will not check to see if you want to discard unsaved changes before throwing away the current session*.

```python 
save_dir = Path("D:\\temp\\laser")
client = ApiClient()

client.project.open(save_dir / "test.lsrwk")
```

Creating a new project.  *Be warned, the API will not check to see if you want to discard unsaved changes before throwing away the current session*.

```python 
client = ApiClient()

client.project.new()
```

We can also check the name and the path of the currently open project.

```python 
client = ApiClient()

print(client.project.path())
print(client.project.name())
```

## Work Settings Functions

Work settings functions control things like the selected material, the kerf, and fonts.  They are accessed through the `work_settings` category of the client.

### Materials

The options in the material library can be retrieved and examined.

```python
from laser_util_api import ApiClient, Units

client = ApiClient(units=Units.INCHES)

options = client.work_settings.material_options()
for mat in options:
    print(mat)
    print(f" {mat.category}, {mat.material}, {mat.thickness:0.3f}, {mat.kerf:0.3f}")
```

The active material can be retrieved.

```python
from laser_util_api import ApiClient, Units

client = ApiClient(units=Units.INCHES)
active = client.work_settings.active_material()
print(active)
```

Finally, any material option object can be set as active.

```python
from laser_util_api import ApiClient, Units

client = ApiClient(units=Units.INCHES)

options = client.work_settings.material_options()

# Just set the last one active, as an example.
options[-1].set_active()
```

### Kerf

The kerf is the width of the cut made by the laser.  Boundaries are offset by half of the kerf width before they're cut.  The kerf is a property of the active material option, but it can be overridden in the software to make small adjustments.  A larger kerf makes a larger part, while a smaller kerf makes a smaller part.

The kerf can be read directly, and will come through in the client's units.

```python
client = ApiClient(units=Units.INCHES)

print(client.work_settings.kerf)
```

The kerf override can be read and set as if it were a property of `client.work_settings`.

```python
client = ApiClient(units=Units.INCHES)

print(client.work_settings.kerf_override)

client.work_settings.kerf_override = True
```

The kerf can only be set if it is overridden.  Setting the kerf is straightforward, but will throw an exception if the kerf override is not active.

```python
client = ApiClient(units=Units.INCHES)

# This will throw an exception if the kerf override is not on
client.work_settings.kerf = 0.1
```

### Fonts

In the work settings there is a library of fonts used for etching.  Each font has an integer ID number, a font family, and a font size.  Fonts are referenced by their ID when creating a text etch element, allowing all text with that font ID to be adjusted at once.  Fonts can be examined, modified, added, and removed through the API.

Getting a list of the active font options is done as follows:

```python
client = ApiClient()

fonts = client.work_settings.fonts()
for font in fonts:
    print(font)
```

Each font item allows the family and size to be edited.  The family is set as a string of the family name, if the family name does not exist on the system setting it will throw an exception.

```python
client = ApiClient()

font = client.work_settings.fonts()[0]
font.size = 16
font.family = "Courier New"
```

The list of valid font family names on the system can be retrieved as shown:

```python
client = ApiClient()

for name in client.work_settings.get_system_font_families():
    print(name)
```

A new font can be created using the `create_font` method, and then edited the same way as any other font.

```python
client = ApiClient()

font = client.work_settings.create_font()
font.size = 20
```

A font can be located by its ID.  If the ID does not exist, an exception will be thrown.

```python
client = ApiClient()

font = client.work_settings.find_font(2)
```

A font can be deleted if it is not the last font left.

```python
client = ApiClient()

font = client.work_settings.find_font(2)
font.delete()
```

### Listing and Editing Existing Project Items

Project items based on the common workspace entity format can be listed and modified from the API.  These are typically project items which have a name, origin, visibility, etc.

```python
import math
from laser_util_api import ApiClient, Xyr

client = ApiClient()
items = client.project_items()

# Print out the existing project tree items
for item in items:
    print(item)

# Grab the first item (assuming there's at least one) and change its name
working = next(items)
working.name = "Name Changed from API"

# Change the value of its origin position
working.origin = Xyr(100, 200, math.pi / 2)

# Set the parent of the origin to the last item in the list (assuming there's more than one)
working.origin_parent = items[-1]

# Finally, set the origin parent back to the workspace origin
working.origin_parent = None

# We can also delete an item with the delete method
working.delete()

```

### The Scratch Workspaces

There are two scratch workspaces where you can create boundary loops and bodies.  These workspaces are created when the client connects to the application and are disposed when the client disconnects.  Things created in the scratch workspaces are unique to the client and not preserved between sessions.

Items in the scratch workspace can be used to create project items.

#### Loops

There are several ways of creating boundary loops in the scratch workspace.  Each will return a `LoopHandle` object, which will allow further modifications to the loop.

```python
from laser_util_api import ApiClient, Vector

client = ApiClient()

# Create a rectangle whose top-left corner is at x=1, y=2, with width=3 and height=4
rect = client.scratch.loops.rectangle(Vector(1, 2), 3, 4)

# Create a rounded rectangle of the same parameters, but with corner radius 0.25
rnd_rect = client.scratch.loops.rounded_rectangle(Vector(1, 2), 3, 4, 0.25)

# Create a circle at x=1, y=2, with radius=3
circle = client.scratch.loops.circle(Vector(1, 2), 3)

# Reverse the circle direction, turning it into a negative boundary
circle.reverse()

# Create an empty loop, then use the cursor to insert a pill shape.  Each element added to the boundary (segment or
# arc) has the *start* point defined, and will run until it hits the start point of the *next* element.  For arcs, the
# circle center must be equidistant from the arc start point and the start point of the next element.
pill = client.scratch.loops.create()
pill.insert_seg_abs(Vector(0, 0))
pill.insert_arc_abs(Vector(1, 0), Vector(1, 1), False)
pill.insert_seg_abs(Vector(1, 2))
pill.insert_arc_abs(Vector(0, 2), Vector(0, 1), False)
```

#### Bodies

A body can be created from an initial boundary loop (must be positive), and then modified through shape operations performed with more boundary loops.

To create a basic boundary loop, first let's use a circle.

```python
from laser_util_api import ApiClient, Vector

client = ApiClient()

# Create a circle boundary at 0, 0 with radius 1
circle = client.scratch.loops.circle(Vector(0, 0), 1)

# Now create a body from the circle.
body = client.scratch.bodies.create(circle)

# Now create a rectangular cut to take out of it.
cut0 = client.scratch.loops.rectangle(Vector(0, -0.5), 2, 1)
cut0.reverse()
body.operate(cut0)

# Now create a positive protrusion to add to the top
pos0 = client.scratch.loops.circle(Vector(0, 1), 0.375)
body.operate(pos0)
```

## Creating a Body Project Item

Creating an actual project item from a body can be done using either a loop or a body.  Both will be immutable after creation, but will persist after the client program ends.

```python
from laser_util_api import ApiClient, Vector

client = ApiClient()

# Create a circle boundary at 0, 0 with radius 1
circle = client.scratch.loops.circle(Vector(0, 0), 1)

# Create a circle body project item from the circle loop.
circle_body = client.create_body(circle)
circle_body.name = "Body Item from Boundary Loop"

# Now we'll create a body with a cut from the circle and use it to create a more complex body project item
body = client.scratch.bodies.create(circle)
cut0 = client.scratch.loops.rectangle(Vector(0, -0.5), 2, 1)
cut0.reverse()
body.operate(cut0)

complex_body = client.create_body(body)
complex_body.name = "Body Item from Body"
```

## Creating and Editing an Etch Project Item

Etch project items can have text and lines.  The following is an example of creating graduated scale marks.

```python
from laser_util_api import ApiClient, Vector, Units

client = ApiClient(units=Units.INCHES)

# Create the etch entity
etch = client.create_etch()
etch.name = "Example Etch Markings"

# From a corner at 1, 2 inches, we'll put marks every 1/2 inch
corner = Vector(1, 2)

for i in range(5):
    mark = corner + Vector(0.5, 0) * i
    
    # Create a vertical line starting at the mark point, 0.25 in tall, with a width of 0.01 inches
    etch.add_line(mark, mark + Vector(0, 0.25), 0.01)
    
    # Create a text item horizontally centered at the mark, up 0.25 inches. See the
    # function documentation for details
    etch.add_text(mark - Vector(0, 0.25), 0, f"{i + 1}", 1, 1, 1)
```




