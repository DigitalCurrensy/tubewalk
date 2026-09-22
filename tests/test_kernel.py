"""TUBEWALK kernel tests. Catalog freeze. W1 scores catalog ok. Not a walk."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tubewalk.tube import walk  # noqa: E402
from tubewalk.tubes import GRAIL, MHP, MTP  # noqa: E402


class WalkTests(unittest.TestCase):
    def test_dark_first(self) -> None:
        self.assertEqual(walk(5, 80, "conduit", False), "pinch")
        self.assertEqual(walk(45, 10, "conduit", False), "stub")
        self.assertEqual(walk(45, 80, "none", False), "dark")
        self.assertEqual(walk(None, 80, None, False), "dark")
        self.assertEqual(walk(45, 80, "conduit", True), "clutter")
        self.assertEqual(walk(45, 30, "conduit", False), "ok")
        self.assertEqual(walk(10, 30, "second", False), "ok")
        self.assertEqual(walk(None, 50_000, "second", False), "ok")
        self.assertEqual(walk(45, None, "conduit", False), "ok")

    def test_catalog_named_not_scored_as_wave0_verdict(self) -> None:
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
            "ok",
        )

    def test_grail_not_this_catalog(self) -> None:
        self.assertFalse(GRAIL["this_catalog"])
        self.assertFalse(GRAIL["is_radar"])


if __name__ == "__main__":
    unittest.main()
