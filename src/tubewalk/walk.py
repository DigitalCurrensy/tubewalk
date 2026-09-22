"""One bad tube. Mare Tranquillitatis west conduit walked. RaySAR named, not run. GRAIL named, not radar."""

from __future__ import annotations

import math

from .tube import walk
from .tubes import MHP, MTP

MOON_RADIUS_M = 1_737_400

MTP_WALK = {
    "id": "TUBE-MTP-WEST",
    "lat": 8.3355,
    "lon": 33.222,
    "frame": "Carrer et al. Nat. Astron. 2024 Mini-RF",
    "wagner": (8.336, 33.222),
    "carrer_m": 15,
    "west_void_m": 40,
    "width_m": 45.0,
    "width_unc_m": 7.5,
    "length_m": 30.0,
    "length_hi_m": 80.0,
    "depth_lo_m": 135.0,
    "depth_hi_m": 175.0,
    "raysar": True,
    "raysar_run": False,
    "grail_is_radar": False,
}

RAYSAR = {
    "name": "RaySAR",
    "engine": "adapted POV-Ray geometric-optics ray tracer",
    "cite": "Auer, Bamler, Reinartz IGARSS 2016 6730-6733",
    "scene_year": 2010,
    "invert_year": 2024,
    "run": False,
    "vendored": False,
    "is_tube_py": False,
}

GRAIL_INV = {
    "model": "GRGM1200A",
    "degree": 1200,
    "resolution_km": 4.5,
    "cannot_resolve_m": 45,
    "marius_hills": (14.0, 302.0),
    "length_km": 60,
    "is_radar": False,
    "fetched": False,
}


def lunar_offset_m(a: tuple[float, float], b: tuple[float, float]) -> float:
    to_r = math.pi / 180.0
    p1, p2 = a[0] * to_r, b[0] * to_r
    dp = (b[0] - a[0]) * to_r
    dl = (b[1] - a[1]) * to_r
    s = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * MOON_RADIUS_M * math.asin(min(1.0, math.sqrt(s)))


def score_published() -> str:
    return walk(MTP["width_m"], MTP["length_m"], MTP["echo"], MTP["clutter"])


def score_mhp() -> str:
    return walk(MHP["width_m"], MHP["length_m"], MHP["echo"], MHP["clutter"])
