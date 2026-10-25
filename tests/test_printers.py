import json
from pathlib import Path

import pytest

from conftest import ascii_stl_cube
from print3d.cli import build_parser
from print3d.dfm import DfmError
from print3d.fits import load_fits, save_fits
from print3d.paths import default_profiles_dir, selected_printer
from print3d.pipeline import run_job
from print3d.printers import profile_details


def test_selection_and_explicit_override(monkeypatch):
    monkeypatch.delenv("PRINT3D_PRINTER", raising=False)
    assert selected_printer() == "x2d"
    monkeypatch.setenv("PRINT3D_PRINTER", "p1s")
    assert default_profiles_dir().name == "p1s-0.4"
    assert default_profiles_dir("x2d").name == "x2d-0.4"
    with pytest.raises(ValueError, match="Unknown printer"):
        selected_printer("../other")


@pytest.mark.parametrize("args", [
    ["make", "test"], ["slice", "cube.stl"], ["coupon"], ["status"],
    ["plan", "cube.stl", "cube.3mf"], ["flatten"], ["mcp"], ["setup", "--agent", "codex"],
])
def test_cli_accepts_printer(args):
    assert build_parser().parse_args([*args, "--printer", "p1s"]).printer == "p1s"


def test_pinned_profiles_match_machine_and_process():
    p1s = profile_details(default_profiles_dir("p1s"))
    x2d = profile_details(default_profiles_dir("x2d"))
    assert (p1s["model"], p1s["nozzles"]) == ("Bambu Lab P1S", 1)
    assert p1s["bed_mm"] == [256, 256, 250]  # Studio's usable height, including its reservation.
    assert p1s["layer_height_mm"] == 0.2
    assert not p1s["supports"]
    assert x2d["nozzles"] == 2
    for printer in ("p1s", "x2d"):
        profiles = default_profiles_dir(printer)
        machine = json.loads((profiles / "machine.json").read_text())
        for kind in ("process", "filament"):
            profile = json.loads((profiles / f"{kind}.json").read_text())
            assert machine["name"] in profile["compatible_printers"]


def test_pipeline_uses_selected_build_height_before_slicing(tmp_path, monkeypatch):
    monkeypatch.setenv("PRINT3D_FITS", str(tmp_path / "fits.json"))
    lines = ascii_stl_cube(20).splitlines()
    for i, line in enumerate(lines):
        if line.strip().startswith("vertex"):
            _, x, y, z = line.split()
            lines[i] = f"      vertex {x} {y} {float(z) * 12.75}"
    mesh = tmp_path / "tall.stl"
    mesh.write_text("\n".join(lines))
    with pytest.raises(DfmError, match="exceeds printer bed"):
        run_job("tall part", mesh=mesh, printer="p1s", jobs_dir=tmp_path / "p1s", execute=False)
    report = run_job("tall part", mesh=mesh, printer="x2d", jobs_dir=tmp_path / "x2d", execute=False)
    assert report["printer"]["model"] == "Bambu Lab X2D"
    assert report["dfm"]["ok"]


def test_fit_calibration_is_separate_per_printer(tmp_path, monkeypatch):
    monkeypatch.delenv("PRINT3D_FITS", raising=False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    save_fits({"slide": 0.15}, "p1s")
    assert load_fits("p1s")["clearance_mm"]["slide"] == 0.15
    assert load_fits("x2d")["clearance_mm"]["slide"] == 0.20
    assert load_fits("x2d")["path"] == str(tmp_path / "print3d" / "fits.json")
