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
        self.assertEqual(proc.returncode, 1, proc.stderr)
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
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(
            proc.stdout.splitlines(),
            [
                "missing width=bad length=80 echo=conduit clutter=false",
                "missing width=45 length=80 echo=conduit clutter=bad",
                "dark width=45 length=80 echo=NONE clutter=false",
            ],
        )


class CloudSpanTests(unittest.TestCase):
    def test_span_drops_noise_and_keeps_the_box(self) -> None:
        from tubewalk.lidar import cloud_line, reduce_cloud

        rows = [
            {"x": "0", "y": "0", "z": "0", "return": "1", "class": "2"},
            {"x": "40", "y": "0", "z": "0", "return": "1", "class": "2"},
            {"x": "0", "y": "12", "z": "0", "return": "1", "class": "2"},
            {"x": "40", "y": "12", "z": "5", "return": "1", "class": "2"},
            {"x": "20", "y": "100", "z": "1", "return": "1", "class": "7"},
            {"x": "nan", "y": "1", "z": "1", "return": "1", "class": "2"},
        ]
        scored = reduce_cloud(rows)
        self.assertEqual(scored["word"], "ok")
        self.assertEqual(scored["points"], 4)
        self.assertEqual(scored["dropped"], 2)
        self.assertEqual(scored["width"], 12)
        self.assertEqual(scored["length"], 40)
        self.assertFalse(scored["clutter"])
        self.assertEqual(
            cloud_line(scored),
            "ok points=4 dropped=2 width=12 length=40 echo=return clutter=false",
        )

    def test_secondary_return_is_clutter_and_a_short_cloud_is_missing(self) -> None:
        from tubewalk.lidar import reduce_cloud

        cluttered = reduce_cloud(
            [
                {"x": "0", "y": "0", "z": "0", "return": "1"},
                {"x": "40", "y": "12", "z": "1", "return": "2"},
            ]
        )
        self.assertEqual(cluttered["word"], "clutter")
        self.assertEqual(reduce_cloud([{"x": "1", "y": "2", "z": "3"}])["word"], "missing")

    def test_example_cloud_prints_the_span(self) -> None:
        import subprocess

        repo = Path(__file__).resolve().parents[1]
        proc = subprocess.run(
            [sys.executable, "-m", "tubewalk", "lidar", str(repo / "examples" / "cloud.csv")],
            cwd=repo,
            env={**__import__("os").environ, "PYTHONPATH": str(repo / "src")},
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(
            proc.stdout.strip(),
            "ok points=4 dropped=1 width=12 length=40 echo=return clutter=false",
        )


class ClothAndSectionTests(unittest.TestCase):
    def test_spike_is_not_ground_and_the_circle_is_not_the_box(self) -> None:
        import subprocess

        repo = Path(__file__).resolve().parents[1]
        env = {**__import__("os").environ, "PYTHONPATH": str(repo / "src")}

        def run(args: list[str], code: int = 0) -> str:
            proc = subprocess.run(
                [sys.executable, "-m", "tubewalk", *args],
                cwd=repo, env=env, capture_output=True, text=True, check=False,
            )
            self.assertEqual(proc.returncode, code, proc.stderr)
            return proc.stdout.strip()

        self.assertEqual(
            run(["cloth", str(repo / "examples" / "ground.csv")]),
            "ground=8 other=1 class2=8 class1=0 class7=0 class18=1 resolution=1 threshold=0.5 cut=file",
        )
        self.assertEqual(
            run(["lidar", str(repo / "examples" / "tube.csv")], 1),
            "stub points=8 dropped=0 width=40 length=12 echo=return clutter=false",
        )
        self.assertEqual(
            run(["section", str(repo / "examples" / "tube.csv")]),
            "ok sections=2 segments=2 points=8 dropped=0 width=12 length=40 closure=0 offset=0 rms=0 echo=return clutter=false",
        )

    def test_slope_keeps_a_step_and_not_the_spike(self) -> None:
        from tubewalk.cloth import cloth_mask

        points = [(float(x), float(y), 0.0) for x in range(3) for y in range(3)]
        points[4] = (1.0, 1.0, 10.0)
        points.append((3.0, 1.0, 0.8))
        mask = cloth_mask(points)
        self.assertTrue(mask[-1])
        self.assertFalse(mask[4])

    def test_bend_is_longer_than_the_chord(self) -> None:
        from tubewalk.section import section_score

        def ring(cx: float, cy: float) -> list[tuple[float, float, float]]:
            return [(cx + 6, cy, 0.0), (cx - 6, cy, 0.0), (cx, cy, 6.0), (cx, cy, -6.0)]

        points = ring(0, 0) + ring(0, 30) + ring(40, 30)
        scored = section_score(points)
        self.assertEqual(scored["width"], 12)
        self.assertEqual(scored["length"], 70)
        self.assertEqual(scored["closure"], 20)
        self.assertEqual(scored["offset"], 24)
        self.assertEqual(scored["segments"], 3)
        self.assertEqual(scored["rms"], 0)
        self.assertEqual(scored["word"], "ok")

    def test_las_12_format_0_round_trip(self) -> None:
        import struct
        import tempfile

        from tubewalk.las import read_las

        scale = 0.001
        tube = [(6, 0, 0, 1, 2), (-6, 0, 0, 1, 2), (0, 0, 6, 1, 2), (0, 0, -6, 1, 2),
                (6, 40, 0, 1, 2), (-6, 40, 0, 1, 2), (0, 40, 6, 1, 2), (0, 40, -6, 1, 2),
                (0, 20, 100, 1, 7)]
        header = bytearray(227)
        header[0:4] = b"LASF"
        header[24] = 1
        header[25] = 2
        struct.pack_into("<H", header, 94, 227)
        struct.pack_into("<I", header, 96, 227)
        struct.pack_into("<I", header, 100, 0)
        header[104] = 0
        struct.pack_into("<H", header, 105, 20)
        struct.pack_into("<I", header, 107, len(tube))
        struct.pack_into("<3d", header, 131, scale, scale, scale)
        body = bytearray()
        for x, y, z, ret, klass in tube:
            body += struct.pack(
                "<3iHBBbBH",
                int(round(x / scale)), int(round(y / scale)), int(round(z / scale)),
                0, ret, klass, 0, 0, 0,
            )
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "tube.las"
            path.write_bytes(bytes(header) + bytes(body))
            got = read_las(path)
            self.assertEqual(len(got), 9)
            self.assertEqual(got[-1][4], 7)
            self.assertAlmostEqual(got[0][0], 6.0, places=6)
            repo = Path(__file__).resolve().parents[1]
            proc = subprocess_run(path, repo)
            bad = path.with_name("bad.las")
            bad.write_bytes(b"not a las file")
            with self.assertRaises(ValueError):
                read_las(bad)
        self.assertEqual(
            proc,
            "ok sections=2 segments=2 points=8 dropped=0 width=12 length=40 closure=0 offset=0 rms=0 echo=return clutter=false",
        )

    def test_laz_round_trip_uses_the_same_circle(self) -> None:
        import tempfile

        import laspy
        import numpy

        from tubewalk.las import read_laz

        xs, ys, zs, klass = [], [], [], []
        for cx, cy in ((0.0, 0.0), (0.0, 40.0)):
            for x, y, z in ((cx + 6, cy, 0.0), (cx - 6, cy, 0.0), (cx, cy, 6.0), (cx, cy, -6.0)):
                xs.append(x)
                ys.append(y)
                zs.append(z)
                klass.append(2)
        xs.append(0.0)
        ys.append(20.0)
        zs.append(100.0)
        klass.append(7)
        cloud = laspy.create(point_format=0, file_version="1.2")
        cloud.x = numpy.array(xs)
        cloud.y = numpy.array(ys)
        cloud.z = numpy.array(zs)
        cloud.classification = numpy.array(klass, dtype="u1")
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "tube.laz"
            cloud.write(path)
            self.assertEqual(read_laz(path)[-1][4], 7)
            text = subprocess_run(path, Path(__file__).resolve().parents[1])
        self.assertEqual(
            text,
            "ok sections=2 segments=2 points=8 dropped=0 width=12 length=40 closure=0 offset=0 rms=0 echo=return clutter=false",
        )

    def test_chunk_table_matches_the_file_and_class_18_survives(self) -> None:
        import io
        import tempfile

        import laspy
        import lazrs
        import numpy

        from tubewalk.las import read_chunk_table, read_laz

        cloud = laspy.create(point_format=6, file_version="1.4")
        cloud.x = numpy.array([0.0, 1.0, 2.0])
        cloud.y = numpy.array([0.0, 0.0, 0.0])
        cloud.z = numpy.array([0.0, 0.0, 10.0])
        cloud.classification = numpy.array([2, 2, 18], dtype="u1")
        cloud.return_number = numpy.array([1, 1, 9], dtype="u1")
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "six.laz"
            cloud.write(path)
            blob = path.read_bytes()
            offset = int.from_bytes(blob[96:100], "little")
            header_size = int.from_bytes(blob[94:96], "little")
            user_at = blob.find(b"laszip encoded")
            vlr_start = user_at - 2
            rec_len = int.from_bytes(blob[vlr_start + 20 : vlr_start + 22], "little")
            data = blob[vlr_start + 54 : vlr_start + 54 + rec_len]
            src = io.BytesIO(blob)
            src.seek(offset)
            theirs = [
                (int(count), int(size))
                for count, size in lazrs.read_chunk_table(src, lazrs.LazVlr(data))
            ]
            self.assertEqual(read_chunk_table(path), theirs)
            self.assertGreater(header_size, 0)
            got = read_laz(path)
            self.assertEqual(got[-1][3], 9)
            self.assertEqual(got[-1][4], 18)

    def test_range_coder_round_trips_signed_deltas(self) -> None:
        from tubewalk.range_coder import decode_deltas, encode_deltas

        values = [0, 1, -1, 12, -40, 1000, -1000]
        self.assertEqual(decode_deltas(encode_deltas(values)), values)
        from tubewalk.range_coder import decode_context, encode_context

        symbols = [0, 1, 2, 255, 3, 3, 3, 40]
        self.assertEqual(decode_context(encode_context(symbols)), symbols)
        from tubewalk.range_coder import decode_bits, encode_bits
        from tubewalk.cloth import classify

        self.assertEqual(decode_bits(encode_bits([0, 1, -1, 2, 40, -30, 1000, 0])), [0, 1, -1, 2, 40, -30, 1000, 0])
        pit = [(x, y, -5.0 if (x, y) == (1, 1) else 0.0) for x in range(3) for y in range(3)]
        classes = classify(pit)
        self.assertEqual(classes[pit.index((1, 1, -5.0))], 7)
        from tubewalk.asprs import (
            asprs_name,
            classification_flags,
            decode_point14,
            encode_point14,
            point14_instance,
        )

        self.assertEqual(asprs_name(2), "ground")
        self.assertEqual(asprs_name(8), "reserved")
        self.assertEqual(asprs_name(12), "reserved")
        self.assertEqual(asprs_name(18), "high noise")
        self.assertEqual(asprs_name(22), "temporal exclusion")
        self.assertEqual(asprs_name(63), "reserved")
        self.assertEqual(asprs_name(64), "user")
        self.assertEqual(classification_flags(key_point=True), 2)
        self.assertEqual(point14_instance(2, 1, 1), 5)
        self.assertEqual(point14_instance(2, 2, 3), 4)
        self.assertEqual(point14_instance(40, 1, 1), 17)
        points = [(2, 1, 1), (2, 1, 1), (7, 2, 2), (18, 1, 1)]
        returns = [(point[1], point[2]) for point in points]
        self.assertEqual(decode_point14(encode_point14(points), returns), [2, 2, 7, 18])
        from tubewalk.asprs import SEED, decode_chunks, encode_chunks

        self.assertEqual(SEED, 1)
        band = [(0, 0, 0.0), (1, 0, 0.0), (0, 1, 0.0), (1, 1, 1.2)]
        self.assertEqual(classify(band)[-1], 4)
        one = [(2, 1, 1), (2, 1, 1)]
        two = [(7, 2, 2), (18, 1, 1)]
        pulses = [[(p[1], p[2]) for p in one], [(p[1], p[2]) for p in two]]
        self.assertEqual(decode_chunks(encode_chunks([one, two]), pulses), [[2, 2], [7, 18]])
        import struct
        from tubewalk.asprs import decode_laz_index, encode_laz_index

        blob = encode_laz_index([one, two])
        table_at = struct.unpack_from("<q", blob, 0)[0]
        version, count = struct.unpack_from("<II", blob, table_at)
        first_count, first_size = struct.unpack_from("<ii", blob, table_at + 8)
        self.assertEqual((version, count, first_count), (0, 2, 2))
        self.assertGreater(first_size, 0)
        self.assertEqual(decode_laz_index(blob, pulses), [[2, 2], [7, 18]])
        from tubewalk.integer import decode_table, encode_table

        one = encode_table([(None, 109)])
        self.assertEqual(one.hex(), "00000000010000003cd8000000")
        self.assertEqual(decode_table(one, False), [(None, 109)])
        two = encode_table([(None, 100), (None, 80)])
        self.assertEqual(two.hex(), "00000000020000003c4e11000000")
        self.assertEqual(decode_table(two, False), [(None, 100), (None, 80)])
        varied = [(6, 109), (4, 80), (8, 200)]
        self.assertEqual(decode_table(encode_table(varied), True), varied)

    def test_las_14_format_6_round_trip(self) -> None:
        import struct
        import tempfile

        from tubewalk.las import read_las

        scale = 0.001
        tube = [(6, 0, 0, 1, 2), (-6, 0, 0, 1, 2), (0, 0, 6, 1, 2), (0, 0, -6, 1, 2),
                (6, 40, 0, 1, 2), (-6, 40, 0, 1, 2), (0, 40, 6, 1, 2), (0, 40, -6, 1, 2),
                (0, 20, 100, 1, 7)]
        header = bytearray(375)
        header[0:4] = b"LASF"
        header[24] = 1
        header[25] = 4
        struct.pack_into("<H", header, 94, 375)
        struct.pack_into("<I", header, 96, 375)
        header[104] = 6
        struct.pack_into("<H", header, 105, 30)
        struct.pack_into("<3d", header, 131, scale, scale, scale)
        struct.pack_into("<Q", header, 247, len(tube))
        body = bytearray()
        for x, y, z, ret, klass in tube:
            body += struct.pack(
                "<3iHHBBhHd",
                int(round(x / scale)), int(round(y / scale)), int(round(z / scale)),
                0, ret, klass, 0, 0, 0, 0.0,
            )
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "tube14.las"
            path.write_bytes(bytes(header) + bytes(body))
            self.assertEqual(read_las(path)[-1][4], 7)
            text = subprocess_run(path, Path(__file__).resolve().parents[1])
        self.assertEqual(
            text,
            "ok sections=2 segments=2 points=8 dropped=0 width=12 length=40 closure=0 offset=0 rms=0 echo=return clutter=false",
        )

    def test_las_14_formats_keep_their_record_rules(self) -> None:
        import struct
        import tempfile

        from tubewalk.las import POINT14, RECORD, read_las

        self.assertEqual(
            [RECORD[fmt] for fmt in range(11)],
            [20, 28, 26, 34, 57, 63, 30, 36, 38, 59, 67],
        )
        self.assertEqual(POINT14[10], 67)

        def write(fmt: int, ret: int, klass: int, minor: int = 4) -> Path:
            length = RECORD[fmt]
            header_size = 375 if minor == 4 else 227
            header = bytearray(header_size)
            header[0:4] = b"LASF"
            header[24] = 1
            header[25] = minor
            struct.pack_into("<H", header, 94, header_size)
            struct.pack_into("<I", header, 96, header_size)
            header[104] = fmt
            struct.pack_into("<H", header, 105, length)
            struct.pack_into("<3d", header, 131, 0.001, 0.001, 0.001)
            point = bytearray(length)
            struct.pack_into("<3i", point, 0, 1000, 0, 0)
            if fmt >= 6:
                struct.pack_into("<H", point, 14, ret)
                point[16] = klass
                if minor == 4:
                    struct.pack_into("<Q", header, 247, 1)
            else:
                point[14] = ret
                point[15] = klass
                if minor == 4:
                    struct.pack_into("<Q", header, 247, 1)
                else:
                    struct.pack_into("<I", header, 107, 1)
            path = Path(folder) / f"f{fmt}.las"
            path.write_bytes(bytes(header) + bytes(point))
            return path

        with tempfile.TemporaryDirectory() as raw:
            folder = Path(raw)
            legacy = read_las(write(5, 0b1001, 2))
            self.assertEqual(legacy, [(1.0, 0.0, 0.0, 1, 2)])
            modern = read_las(write(10, 9, 18))
            self.assertEqual(modern, [(1.0, 0.0, 0.0, 9, 18)])
            bad_version = write(6, 1, 2, minor=2)
            with self.assertRaises(ValueError):
                read_las(bad_version)
            short = write(8, 1, 2)
            blob = bytearray(short.read_bytes())
            struct.pack_into("<H", blob, 105, 37)
            short.write_bytes(bytes(blob))
            with self.assertRaises(ValueError):
                read_las(short)


def subprocess_run(path: Path, repo: Path) -> str:
    import subprocess
    proc = subprocess.run(
        [sys.executable, "-m", "tubewalk", "las", str(path)],
        cwd=repo,
        env={**__import__("os").environ, "PYTHONPATH": str(repo / "src")},
        capture_output=True, text=True, check=False,
    )
    if proc.returncode != 0:
        raise AssertionError(proc.stderr)
    return proc.stdout.strip()


if __name__ == "__main__":
    unittest.main()
