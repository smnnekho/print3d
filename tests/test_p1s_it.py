"""Real Blender + Studio coverage of the P1S-specific export, including colours."""
import json
import os
import zipfile
from pathlib import Path

import pytest

from print3d.handoff import build_handoff
from print3d.paths import repo_root
from print3d.pipeline import run_job

pytestmark = pytest.mark.skipif(
    os.environ.get("PRINT3D_STUDIO_IT") != "1", reason="Set PRINT3D_STUDIO_IT=1 for Blender + Studio"
)


def test_p1s_colour_inlay_and_handoff(tmp_path, monkeypatch):
    monkeypatch.setenv("PRINT3D_PRINTER", "x2d")
    monkeypatch.setenv("PRINT3D_FITS", str(tmp_path / "fits.json"))
    report = run_job("P1S colour strip", printer="p1s",
                     script=repo_root() / "examples" / "p1s_colour_strip.py", jobs_dir=tmp_path)
    assert report["status"] == "ready_for_review", report["advice"]
    assert report["printer"]["nozzles"] == 1
    assert {f["color"] for f in report["filaments"] if f["used_g"] > 0} == {"white", "blue"}
    assert any(a["code"] == "colours" and "1 nozzle" in a["message"] and "AMS" in a["fix"]
               for a in report["advice"])
    with zipfile.ZipFile(report["open_in_studio"]) as z:
        settings = json.loads(z.read("Metadata/project_settings.config"))
        assert settings["printer_model"] == "Bambu Lab P1S"
        assert settings["nozzle_diameter"] == ["0.4"]
        assert len(settings["filament_type"]) == 2
    handoff = build_handoff(Path(report["job_dir"]), currency="EUR", render=False)
    sheets = list((Path(report["job_dir"]) / "handoff").glob("*.html"))
    assert sheets and handoff
    sheet = next(p.read_text() for p in sheets if "<h1>" in p.read_text())
    assert "Bambu Lab P1S" in sheet
    assert "Bambu Lab X2D" not in sheet
