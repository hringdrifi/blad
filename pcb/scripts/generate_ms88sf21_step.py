"""Generate the project-local MS88SF21 STEP model with FreeCAD."""

from pathlib import Path

import FreeCAD as App
import Import
import Part


OUTPUT = Path(__file__).resolve().parents[1] / "smidr.3dshapes" / "MS88SF21.step"


def add_part(doc, name, label, shape, color):
    obj = doc.addObject("PartDesign::Feature", name)
    obj.Label = label
    obj.Shape = shape
    if obj.ViewObject is not None:
        obj.ViewObject.ShapeColor = color
    return obj


doc = App.newDocument("MS88SF21")

# The model origin and orientation match the footprint: pin 1 is on the left,
# nearest the PCB antenna. Dimensions are from MinewSemi's nRF52840 datasheet.
board = Part.makeBox(17.4, 23.2, 0.8, App.Vector(-8.7, -11.6, 0.0))
add_part(doc, "ModulePCB", "MS88SF21 PCB", board, (0.05, 0.32, 0.12))

# Castellated terminal metal. The land pattern extends farther outward on the
# carrier PCB; these solids represent only the module-side contacts.
for index in range(14):
    y = -4.41 + index * 1.1
    left = Part.makeBox(1.2, 0.8, 0.82, App.Vector(-8.7, y, 0.0))
    right = Part.makeBox(1.2, 0.8, 0.82, App.Vector(7.5, y, 0.0))
    add_part(doc, f"Pad{index + 1:02d}", f"Pad {index + 1}", left, (0.78, 0.60, 0.12))
    add_part(doc, f"Pad{28 - index:02d}", f"Pad {28 - index}", right, (0.78, 0.60, 0.12))

# Shield dimensions are simplified from the manufacturer's mechanical view;
# the overall assembled height remains the specified 2.0 mm.
shield = Part.makeBox(14.6, 16.0, 1.15, App.Vector(-7.3, -4.75, 0.8))
add_part(doc, "Shield", "RF shield", shield, (0.68, 0.70, 0.72))

# Pin-1 orientation mark on the top of the shield.
pin1_mark = Part.makeCylinder(0.55, 0.03, App.Vector(-6.1, -3.55, 1.95))
add_part(doc, "Pin1Mark", "Pin 1 mark", pin1_mark, (0.12, 0.12, 0.12))

# A lightweight representation of the PCB trace antenna. It is intentionally
# separate from the shield so the antenna end is obvious in the 3D viewer.
antenna_segments = [
    (-7.1, -10.7, 13.8, 0.45),
    (-7.1, -10.7, 0.45, 3.5),
    (-7.1, -7.65, 4.0, 0.45),
    (-3.55, -9.2, 0.45, 2.0),
    (-3.55, -9.2, 7.0, 0.45),
    (3.0, -10.7, 0.45, 1.95),
    (3.0, -10.7, 4.1, 0.45),
    (6.65, -10.7, 0.45, 3.5),
]
for index, (x, y, width, length) in enumerate(antenna_segments, start=1):
    trace = Part.makeBox(width, length, 0.04, App.Vector(x, y, 0.8))
    add_part(doc, f"Antenna{index}", "PCB antenna", trace, (0.78, 0.60, 0.12))

doc.recompute()
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
Import.export(doc.Objects, str(OUTPUT))
App.closeDocument(doc.Name)

check = Part.Shape()
check.read(str(OUTPUT))
bounds = check.BoundBox
expected = (17.4, 23.2, 1.98)
actual = (bounds.XLength, bounds.YLength, bounds.ZLength)
for measured, target in zip(actual, expected):
    if abs(measured - target) > 0.01:
        raise RuntimeError(f"Unexpected STEP bounds: {actual}")
print(f"{OUTPUT} bounds={actual}")
