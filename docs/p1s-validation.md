# P1S validation — 2026-10-25

Tested on macOS with Blender 4.4.0, Bambu Studio 02.08.02.61 and Python 3.12.9.
Profiles are taken from the installed official Bambu Studio presets, with
their source recorded under `src/print3d/profiles/p1s-0.4/`.

## Automated checks

- 39 focused tests passed: profile selection, actual build-height enforcement,
  separate fit calibration, MCP overrides, setup preservation and slicer commands.
- The regular suite passed: 91 tests, with 9 existing opt-in integration tests
  skipped. This was run before adding the new P1S integration test below.
- `PRINT3D_STUDIO_IT=1 pytest -q tests/test_p1s_it.py`: 1 passed using real Blender
  and Bambu Studio. It checks two colours with one nozzle, nonzero use of both
  filaments, the AMS advice, the exported P1S project settings and the hand-off
  sheet's printer identity even when the surrounding default is X2D.
- The installed stdio MCP server was started using its exact Codex configuration;
  `printer_status` returned P1S and one nozzle. Other Codex settings were compared
  before and after setup and were unchanged.

## Generated examples

- `examples/nameplate.py`, prompt `a 40mm nameplate that says P1S`: ready for review,
  40 × 16 × 3 mm, 15 layers, 9m 17s and 1.46 g in the slicer estimate.
- `examples/p1s_colour_strip.py`: ready for review, white plate with a visible
  blue inlay, 20.3 minutes and 5.08 g including the slicer's colour-change overhead.

The nameplate `.3mf` was opened in Bambu Studio's Prepare view. The model,
P1S printer, 0.4 mm nozzle, PLA Basic and 0.20 mm process were visually checked.
Both plate images and the nameplate hand-off render were inspected. The generated
print sheet was checked for P1S metadata and valid embedded image references;
browser layout inspection was blocked by the browser's local-file URL policy.

## Remaining physical checks

No print was started and no printer was contacted by print3d. Actual fit,
strength, bed adhesion and AMS operation have not been tested. P1S fit values
remain uncalibrated defaults until a coupon is physically printed and measured.
The retained X2D presets were checked by the unit tests; no X2D hardware or
X2D end-to-end slicing acceptance was performed in this run.
