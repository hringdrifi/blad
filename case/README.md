# Blað case models

This directory contains the STEP models for the Blað case. The models are supplied as separate parts so they can be inspected, modified, or incorporated into a manufacturing workflow.

| File | Role |
| --- | --- |
| [`blad_switch_plate.step`](blad_switch_plate.step) | Switch plate for the case assembly. |
| [`blad_bumper.step`](blad_bumper.step) | Bumper layer between the plate and bottom plate. |
| [`blad_battery_cap.step`](blad_battery_cap.step) | Battery cap for the case assembly. |

## Assembly hardware

- M2 standoffs, 4.5 mm long
- M2 screws, 3 mm long

## Use

Import all three STEP files into the same CAD assembly and align them by their native coordinates. The models are design data rather than a production-ready manufacturing package: confirm dimensions, fit with the PCB and components, material selection, tolerances, and manufacturing constraints before fabrication.

The case models are licensed under the [CERN Open Hardware Licence Version 2 - Permissive (CERN-OHL-P-2.0)](../LICENSE).
