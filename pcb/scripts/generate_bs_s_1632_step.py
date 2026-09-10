"""Generate a KiCad-aligned STEP model for the Takachi BS-S-1632.

The controlling dimensions come from Takachi drawing BS-S-1632.pdf (2025-06-17
revision).  Small press-tool radii and the exact spring forming profile are not
dimensioned, so those details are represented conservatively for PCB clearance
checking rather than manufacturing.
"""

from pathlib import Path

import FreeCAD as App
import Import
import Part


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "smidr.3dshapes" / "Takachi_BS-S-1632.step"

SHEET = 0.25
PCB_TOP = 0.0
TOP_Z = 3.55
METAL = (0.76, 0.78, 0.80)


def add_part(doc, name, label, shape):
    obj = doc.addObject("PartDesign::Feature", name)
    obj.Label = label
    obj.Shape = shape
    if obj.ViewObject is not None:
        obj.ViewObject.ShapeColor = METAL
    return obj


def outline_face():
    # Symmetric plan view.  The extrema and pin axis follow the official drawing:
    # 18.4 mm wide, 15.1 mm long, and 16.9 mm between PCB mounting holes.
    right = [
        (2.80, -8.60),
        (8.45, -2.95),
        (8.45, 2.80),
        (9.20, 3.55),
        (9.20, 4.15),
        (8.85, 5.15),
        (8.10, 5.95),
        (7.05, 6.40),
        (5.85, 6.50),
        (4.85, 6.25),
        (3.95, 5.65),
        (3.10, 5.25),
        (2.10, 5.05),
        (1.05, 5.15),
        (0.00, 5.55),
    ]
    left = [(-x, y) for x, y in reversed(right[1:-1])]
    points = [(-2.80, -8.60), (2.80, -8.60), *right[1:], *left]
    vectors = [App.Vector(x, y, TOP_Z) for x, y in points]
    wire = Part.makePolygon([*vectors, vectors[0]])
    return Part.Face(wire)


def keyhole(center_x):
    circle = Part.makeCylinder(1.72, SHEET + 0.2, App.Vector(center_x, 0.0, TOP_Z - 0.1))
    neck = Part.makeBox(2.25, 4.7, SHEET + 0.2, App.Vector(center_x - 1.125, 0.0, TOP_Z - 0.1))
    return circle.fuse(neck)


def spring_tongue(center_x):
    # The tongue slopes down toward the battery to provide contact force.
    x0 = center_x - 0.82
    profile = Part.makePolygon(
        [
            App.Vector(x0, 0.00, 2.05),
            App.Vector(x0, 4.35, TOP_Z),
            App.Vector(x0, 4.35, TOP_Z + SHEET),
            App.Vector(x0, 0.00, 2.30),
            App.Vector(x0, 0.00, 2.05),
        ]
    )
    tongue = Part.Face(profile).extrude(App.Vector(1.64, 0, 0))
    contact = Part.makeBox(1.64, 0.55, 0.55, App.Vector(x0, -0.25, 1.75))
    return tongue.fuse(contact)


doc = App.newDocument("Takachi_BS_S_1632")

# Main stamped deck, including the two relief openings for the spring fingers.
deck = outline_face().extrude(App.Vector(0, 0, SHEET))
deck = deck.cut(keyhole(-4.05)).cut(keyhole(4.05))
parts = [add_part(doc, "Deck", "Stamped holder deck", deck)]

for index, x in enumerate((-4.05, 4.05), start=1):
    parts.append(add_part(doc, f"Spring{index}", f"Battery spring {index}", spring_tongue(x)))

# Folded side walls and their through-hole pins.  The pin centers are the model
# origin's X axis, matching the footprint holes at +/-8.45 mm.
for side, x in (("Left", -8.45), ("Right", 8.20)):
    wall = Part.makeBox(SHEET, 5.75, TOP_Z + SHEET, App.Vector(x, -2.95, PCB_TOP))
    parts.append(add_part(doc, f"{side}Wall", f"{side.lower()} folded wall", wall))

for side, x in (("Left", -8.575), ("Right", 8.325)):
    pin = Part.makeBox(SHEET, 1.20, 2.70, App.Vector(x, -0.60, -2.70))
    parts.append(add_part(doc, f"{side}Pin", f"{side.lower()} PCB pin", pin))
    toe_x = x - 0.50 if side == "Left" else x
    toe = Part.makeBox(0.75, 1.20, SHEET, App.Vector(toe_x, -0.60, -2.70))
    parts.append(add_part(doc, f"{side}Toe", f"{side.lower()} pin retention bend", toe))

# The narrow end is folded down and provides the visible retaining lip.
front_wall = Part.makeBox(5.60, SHEET, 3.30, App.Vector(-2.80, -8.60, 0.25))
front_lip = Part.makeBox(5.60, 0.70, SHEET, App.Vector(-2.80, -8.60, 0.25))
parts.append(add_part(doc, "FrontWall", "Front retaining wall", front_wall))
parts.append(add_part(doc, "FrontLip", "Front retaining lip", front_lip))

doc.recompute()
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
Import.export(parts, str(OUTPUT))

# Validate the dimensions that matter for PCB placement and enclosure clearance.
compound = Part.makeCompound([obj.Shape for obj in parts])
bounds = compound.BoundBox
actual = (bounds.XLength, bounds.YLength, bounds.ZLength)
expected = (18.4, 15.1, 6.5)
for measured, target in zip(actual, expected):
    if abs(measured - target) > 0.02:
        raise RuntimeError(f"Unexpected STEP bounds: {actual}, expected {expected}")

check = Part.Shape()
check.read(str(OUTPUT))
if check.isNull():
    raise RuntimeError("FreeCAD could not read the generated STEP file")

App.closeDocument(doc.Name)
print(f"{OUTPUT} bounds={actual}")
