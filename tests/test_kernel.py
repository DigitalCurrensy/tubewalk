# Copyright 2026 Digital Currensy Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""TUBEWALK kernel tests. Ok is not a walk."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tubewalk.tube import walk  # noqa: E402
from tubewalk.tubes import GRAIL, MHP, MTP  # noqa: E402
from tubewalk.counsel import COHRAY, INSAR, compile_counsel, fringe_los_m, geometric_optics_valid  # noqa: E402
from tubewalk.letter import MASCONS, SAR_SIM, compile_letter, rasterization_can_invert_ceiling  # noqa: E402
from tubewalk.walk import GRAIL_INV, MTP_WALK, RAYSAR, lunar_offset_m, score_mhp, score_published  # noqa: E402


class WalkTests(unittest.TestCase):
    def test_dark_first(self) -> None:
        self.assertEqual(walk(5, 80, "conduit", False), "pinch")
        self.assertEqual(walk(45, 10, "conduit", False), "stub")
        self.assertEqual(walk(45, 80, "none", False), "dark")
        self.assertEqual(walk(45, 80, "NONE", False), "dark")
        self.assertEqual(walk(45, 80, "", False), "dark")
        self.assertEqual(walk(45, 80, "  none  ", False), "dark")
        self.assertEqual(walk(45, 80, 1, False), "missing")
        self.assertEqual(walk(None, 80, None, False), "dark")
        self.assertEqual(walk(45, 80, "conduit", True), "clutter")
        self.assertEqual(walk(45, 30, "conduit", False), "ok")
        self.assertEqual(walk(10, 30, "second", False), "ok")
        self.assertEqual(walk(None, 50_000, "second", False), "missing")
        self.assertEqual(walk(45, None, "conduit", False), "missing")

    def test_negative_width_or_length_is_missing_and_zero_is_a_number(self) -> None:
        self.assertEqual(walk(-1, 80, "conduit", False), "missing")
        self.assertEqual(walk(45, -1, "conduit", False), "missing")
        self.assertEqual(walk(-1, 80, "none", False), "dark")
        self.assertEqual(walk(0, 80, "conduit", False), "pinch")
        self.assertEqual(walk(0, 0, "conduit", False), "pinch")
        self.assertEqual(walk(10, 0, "conduit", False), "stub")
        self.assertEqual(
            walk(MHP["width_m"], MHP["length_m"], MHP["echo"], MHP["clutter"]),
            "missing",
        )

    def test_named_catalog_is_not_a_fetched_survey(self) -> None:
        self.assertEqual(MTP["id"], "TUBE-MTP-WEST")
        self.assertEqual(MTP["lat"], 8.3355)
        self.assertEqual(MTP["lon"], 33.222)
        self.assertEqual(MTP["width_m"], 45.0)
        self.assertEqual(MTP["length_m"], 30.0)
        self.assertEqual(MTP["echo"], "conduit")
        self.assertFalse(MTP["fetched"])
        self.assertEqual(MHP["id"], "TUBE-MHP-RILLE")
        self.assertEqual(MHP["lat"], 14.1)
        self.assertEqual(MHP["lon"], 303.262)
        self.assertIsNone(MHP["width_m"])
        self.assertEqual(MHP["length_m"], 50_000.0)
        self.assertEqual(MHP["echo"], "second")
        self.assertFalse(MHP["fetched"])
        self.assertEqual(
            walk(MTP["width_m"], MTP["length_m"], MTP["echo"], MTP["clutter"]),
            "ok",
        )
        self.assertEqual(
            walk(MHP["width_m"], MHP["length_m"], MHP["echo"], MHP["clutter"]),
            "missing",
        )

    def test_grail_not_this_catalog(self) -> None:
        self.assertFalse(GRAIL["this_catalog"])
        self.assertFalse(GRAIL["is_radar"])
        self.assertEqual(GRAIL["degree"], 1200)
        self.assertEqual(GRAIL["cannot_resolve_m"], 45)
        self.assertFalse(GRAIL["fetched"])


class Wave2Tests(unittest.TestCase):
    def test_published_ok_is_not_a_walk(self) -> None:
        self.assertEqual(MTP_WALK["id"], "TUBE-MTP-WEST")
        self.assertEqual(score_published(), "ok")
        self.assertEqual(score_mhp(), "missing")
        self.assertFalse(MTP_WALK["raysar_run"])
        self.assertFalse(MTP_WALK["grail_is_radar"])
        self.assertEqual(round(lunar_offset_m((8.3355, 33.222), (8.336, 33.222))), 15)
        with self.assertRaises(ValueError):
            lunar_offset_m((float("nan"), 33.222), (8.336, 33.222))

    def test_raysar_named_not_run(self) -> None:
        self.assertEqual(RAYSAR["name"], "RaySAR")
        self.assertFalse(RAYSAR["run"])
        self.assertFalse(RAYSAR["vendored"])
        self.assertFalse(RAYSAR["is_tube_py"])
        self.assertIn("POV-Ray", RAYSAR["engine"])
        self.assertEqual(RAYSAR["scene_year"], 2010)
        self.assertEqual(RAYSAR["invert_year"], 2024)

    def test_grail_km_scale_not_radar(self) -> None:
        self.assertEqual(GRAIL_INV["model"], "GRGM1200A")
        self.assertEqual(GRAIL_INV["degree"], 1200)
        self.assertEqual(GRAIL_INV["resolution_km"], 4.5)
        self.assertEqual(GRAIL_INV["cannot_resolve_m"], 45)
        self.assertFalse(GRAIL_INV["is_radar"])
        self.assertFalse(GRAIL_INV["fetched"])
        self.assertGreater(GRAIL_INV["resolution_km"] * 1000, GRAIL_INV["cannot_resolve_m"])
        self.assertEqual(GRAIL_INV["length_km"], 60)


class Wave3Tests(unittest.TestCase):
    def test_published_ok_letter_is_not_a_walk(self) -> None:
        letter = compile_letter("walk")
        self.assertEqual(letter["title"], "TUBE LETTER")
        self.assertTrue(letter["issued"])
        self.assertEqual(letter["stamp"], "ok")
        self.assertTrue(letter["do_not_enter"])
        self.assertTrue(letter["not_a_certificate"])
        self.assertLessEqual(letter["words"], 80)
        self.assertIn("ok is not a walk", letter["body"])

    def test_sarsim_named_not_run(self) -> None:
        letter = compile_letter("sarsim")
        self.assertTrue(letter["issued"])
        self.assertEqual(letter["why"], "sarsim_named_not_scored")
        self.assertFalse(letter["sarsim_run"])
        self.assertFalse(rasterization_can_invert_ceiling())
        raysar = next(s for s in SAR_SIM if s["id"] == "raysar")
        sarviz = next(s for s in SAR_SIM if s["id"] == "sarviz")
        self.assertFalse(raysar["run"])
        self.assertFalse(raysar["vendored"])
        self.assertTrue(raysar["can_invert_ceiling"])
        self.assertFalse(sarviz["can_invert_ceiling"])
        self.assertEqual(raysar["bounce_need"], 3)

    def test_mascon_is_not_this_letter(self) -> None:
        letter = compile_letter("mascon")
        self.assertFalse(letter["issued"])
        self.assertEqual(letter["stamp"], "refused")
        self.assertEqual(letter["why"], "not_this_letter")
        self.assertFalse(letter["mascon_is_this_letter"])
        imbrium = next(m for m in MASCONS if m["id"] == "imbrium")
        self.assertEqual(imbrium["anomaly_mgal"], 158)
        self.assertGreater(imbrium["diameter_km"] * 1000, 45)
        self.assertFalse(imbrium["this_letter"])


class Wave4Tests(unittest.TestCase):
    def test_compiled_pass_is_unsigned(self) -> None:
        paper = compile_counsel("compiled")
        self.assertEqual(paper["title"], "TUBE COUNSEL PASS")
        self.assertTrue(paper["issued"])
        self.assertEqual(paper["stamp"], "unsigned")
        self.assertFalse(paper["signed"])
        self.assertFalse(paper["wet_ink"])
        self.assertEqual(paper["counsel"], "unsigned")
        self.assertTrue(paper["not_a_certificate"])
        self.assertTrue(paper["do_not_enter"])
        self.assertLessEqual(paper["words"], 80)
        self.assertIn("ok is not a walk", paper["body"])

    def test_cohras_named_not_run(self) -> None:
        paper = compile_counsel("cohras")
        self.assertFalse(paper["issued"])
        self.assertEqual(paper["why"], "cohras_named_not_scored")
        self.assertFalse(paper["cohras_run"])
        self.assertFalse(COHRAY["run"])
        self.assertFalse(COHRAY["vendored"])
        self.assertTrue(COHRAY["insar"])
        self.assertFalse(COHRAY["lunar"])
        self.assertFalse(COHRAY["is_tube_py"])
        coh = next(s for s in SAR_SIM if s["id"] == "cohras")
        self.assertTrue(coh["insar"])
        self.assertTrue(coh["speckle"])
        self.assertFalse(coh["run"])
        self.assertTrue(geometric_optics_valid(0.126, 45.0))
        self.assertFalse(geometric_optics_valid(45.0, 0.126))

    def test_insar_is_not_a_walk(self) -> None:
        paper = compile_counsel("insar")
        self.assertFalse(paper["issued"])
        self.assertEqual(paper["why"], "insar_is_not_a_walk")
        self.assertFalse(paper["insar_is_walk"])
        self.assertFalse(INSAR["this_walk"])
        self.assertFalse(INSAR["minirf_is_stack"])
        self.assertEqual(INSAR["fringe_s_cm"], 6.3)
        self.assertEqual(INSAR["wavelength_cm"], 12.6)
        self.assertEqual(INSAR["transmitter_failed"], "2010-12-26")
        self.assertEqual(fringe_los_m(0.126), 0.063)
        self.assertIsNone(fringe_los_m(0.0))
        self.assertIsNone(fringe_los_m(float("nan")))
        self.assertIsNone(fringe_los_m(float("inf")))
        self.assertIn("fringe is not a conduit", paper["body"])


class CsvMissingTests(unittest.TestCase):
    def test_blank_numeric_uses_none_branch(self) -> None:
        from tubewalk.__main__ import score_row

        blank_width = score_row(
            {"width_m": "", "length_m": "80", "echo": "conduit", "clutter": "false"}
        )
        blank_length = score_row(
            {"width_m": "45", "length_m": "", "echo": "conduit", "clutter": "false"}
        )
        self.assertEqual(blank_width, walk(None, 80.0, "conduit", False))
        self.assertEqual(blank_length, walk(45.0, None, "conduit", False))
        self.assertEqual(blank_width, "missing")
        self.assertEqual(blank_length, "missing")



class FiniteTubeTests(unittest.TestCase):
    def test_non_finite_is_missing(self) -> None:
        self.assertEqual(walk(float("nan"), 80.0, "conduit", False), "missing")



class PrintedLineTests(unittest.TestCase):
    def test_inputs_are_on_the_line(self) -> None:
        import subprocess
        repo = Path(__file__).resolve().parents[1]
        proc = subprocess.run(
            [sys.executable, "-m", "tubewalk", str(repo / "examples" / "conduit.csv")],
            cwd=repo, env={**__import__("os").environ, "PYTHONPATH": str(repo / "src")},
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(
            proc.stdout.splitlines()[0],
            "ok width=45 length=30 echo=conduit clutter=false",
        )

    def test_bad_cells_print_missing(self) -> None:
        import subprocess
        import tempfile

        repo = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.csv"
            path.write_text(
                "width_m,length_m,echo,clutter\n"
                "abc,80,conduit,false\n"
                "45,80,conduit,maybe\n"
                "45,80,NONE,false\n",
                encoding="utf-8",
            )
            proc = subprocess.run(
                [sys.executable, "-m", "tubewalk", str(path)],
                cwd=repo,
                env={**__import__("os").environ, "PYTHONPATH": str(repo / "src")},
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(
            proc.stdout.splitlines(),
            [
                "missing width=bad length=80 echo=conduit clutter=false",
                "missing width=45 length=80 echo=conduit clutter=bad",
                "dark width=45 length=80 echo=NONE clutter=false",
            ],
        )


if __name__ == "__main__":
    unittest.main()
