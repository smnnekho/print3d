"""Read printer limits and hand-off metadata from the actual slicing profiles."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from print3d.flatten import infer_extruder_count


def profile_details(profiles: Path) -> dict[str, Any]:
    machine, process, filament = (
        json.loads((profiles / f"{kind}.json").read_text(encoding="utf-8"))
        for kind in ("machine", "process", "filament")
    )
    points = [tuple(float(v) for v in point.split("x")) for point in machine["printable_area"]]
    bed = [max(p[i] for p in points) - min(p[i] for p in points) for i in (0, 1)]
    bed.append(float(machine["printable_height"]))
    return {
        "model": machine["printer_model"],
        "profile": machine["name"],
        "nozzles": infer_extruder_count(machine),
        "nozzle_diameter_mm": [float(v) for v in machine["nozzle_diameter"]],
        "bed_mm": bed,
        "layer_height_mm": float(process["layer_height"]),
        "bed_type": process.get("curr_bed_type", "Textured PEI Plate"),
        "supports": str(process.get("enable_support", "0")) == "1",
        "filament": filament["name"],
        "cost_per_kg": float(filament["filament_cost"][0]),
    }
