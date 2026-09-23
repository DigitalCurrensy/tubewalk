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

"""Centerline, then a circle in the cross section. The box is not the diameter."""

from __future__ import annotations

import math

from .tube import walk

BIN_M = 1.0


def _axis(points: list[tuple[float, float, float]]) -> tuple[float, float]:
    mx = sum(p[0] for p in points) / len(points)
    my = sum(p[1] for p in points) / len(points)
    sxx = syy = sxy = 0.0
    for x, y, _z in points:
        dx = x - mx
        dy = y - my
        sxx += dx * dx
        syy += dy * dy
        sxy += dx * dy
    # Largest eigenvector of the 2x2 covariance. A tie keeps X.
    if abs(sxy) < 1e-12 and sxx >= syy:
        return 1.0, 0.0
    if abs(sxy) < 1e-12:
        return 0.0, 1.0
    trace = sxx + syy
    det = sxx * syy - sxy * sxy
    disc = max(0.0, trace * trace / 4.0 - det)
    eigen = trace / 2.0 + math.sqrt(disc)
    vx = sxy
    vy = eigen - sxx
    norm = math.hypot(vx, vy)
    if norm == 0.0:
        return 1.0, 0.0
    return vx / norm, vy / norm


def circle_diameter(uv: list[tuple[float, float]]) -> float | None:
    """Algebraic circle. Diameter is twice the mean radius. Collinear is None."""
    n = len(uv)
    if n < 3:
        return None
    su = sv = suu = svv = suv = suuu = svvv = suuv = suvv = 0.0
    for u, v in uv:
        su += u
        sv += v
        uu = u * u
        vv = v * v
        suu += uu
        svv += vv
        suv += u * v
        suuu += uu * u
        svvv += vv * v
        suuv += uu * v
        suvv += u * vv
    a = n * suu - su * su
    b = n * suv - su * sv
    c = n * svv - sv * sv
    d = 0.5 * (n * suuu + n * suvv - su * (suu + svv))
    e = 0.5 * (n * svvv + n * suuv - sv * (suu + svv))
    det = a * c - b * b
    if abs(det) < 1e-9:
        return None
    uc = (d * c - b * e) / det
    vc = (a * e - b * d) / det
    radius = 0.0
    for u, v in uv:
        radius += math.hypot(u - uc, v - vc)
    return 2.0 * radius / n


def section_score(points: list[tuple[float, float, float]]) -> dict[str, float | int | str | None]:
    """Width is the median station diameter. Length is the centerline extent.

    The centerline is the long axis of the horizontal coordinates. Each 1 m
    station with at least three points gets one circle in the plane of
    (offset, z). Stations that do not fit are skipped. No fitted station is
    missing. Class 7 is not dropped here. A non-finite point is dropped.
    """
    kept = [p for p in points if all(math.isfinite(v) for v in p)]
    dropped = len(points) - len(kept)
    if len(kept) < 3:
        return {
            "word": "missing",
            "points": len(kept),
            "dropped": dropped,
            "width": None,
            "length": None,
            "sections": 0,
        }
    mx = sum(p[0] for p in kept) / len(kept)
    my = sum(p[1] for p in kept) / len(kept)
    ax, ay = _axis(kept)
    px, py = -ay, ax
    stations: dict[int, list[tuple[float, float]]] = {}
    along: list[float] = []
    for x, y, z in kept:
        dx = x - mx
        dy = y - my
        station = dx * ax + dy * ay
        offset = dx * px + dy * py
        along.append(station)
        stations.setdefault(math.floor(station / BIN_M), []).append((offset, z))
    diameters = []
    for group in stations.values():
        diameter = circle_diameter(group)
        if diameter is not None and math.isfinite(diameter):
            diameters.append(diameter)
    if not diameters:
        return {
            "word": "missing",
            "points": len(kept),
            "dropped": dropped,
            "width": None,
            "length": None,
            "sections": 0,
        }
    diameters.sort()
    mid = len(diameters) // 2
    if len(diameters) % 2:
        width = diameters[mid]
    else:
        width = (diameters[mid - 1] + diameters[mid]) / 2.0
    length = max(along) - min(along)
    return {
        "word": walk(width, length, "return", False),
        "points": len(kept),
        "dropped": dropped,
        "width": width,
        "length": length,
        "sections": len(diameters),
    }


def section_line(scored: dict[str, float | int | str | None]) -> str:
    def show(value: float | None) -> str:
        if value is None:
            return "missing"
        return f"{value:.10g}"

    return (
        f"{scored['word']} sections={scored['sections']} points={scored['points']} "
        f"dropped={scored['dropped']} width={show(scored['width'])} "
        f"length={show(scored['length'])} echo=return clutter=false"
    )
