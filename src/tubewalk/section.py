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

LINK_M = 15.0


def circle_fit(uv: list[tuple[float, float]]) -> tuple[float, float] | None:
    """Algebraic circle. Returns diameter and radial RMS. Collinear is None."""
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
    radii = [math.hypot(u - uc, v - vc) for u, v in uv]
    radius = sum(radii) / n
    rms = math.sqrt(sum((item - radius) ** 2 for item in radii) / n)
    if rms > 0.05 * (2.0 * radius):
        return None
    return 2.0 * radius, rms


def circle_diameter(uv: list[tuple[float, float]]) -> float | None:
    fitted = circle_fit(uv)
    if fitted is None:
        return None
    return fitted[0]


def section_score(points: list[tuple[float, float, float]]) -> dict[str, float | int | str | None]:
    """Width is the median station diameter. Length is the path of the centers.

    Points whose plan positions are within 15 m are one station, so a 12 m
    ring stays one station and the next ring, 30 m away, does not. The circle
    is fit in that station's own cross-section. The length is the polyline
    through the station centers, starting at the center with the smallest x.
    A straight tube is one segment. A bend is the sum of the segments, which
    is longer than the chord. `rms` is the largest radial residual. A residual
    above 5% of the diameter is not a circle, and that station is skipped.
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
            "rms": None,
        }
    parent = list(range(len(kept)))

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    for i, left in enumerate(kept):
        for j in range(i + 1, len(kept)):
            right = kept[j]
            if math.hypot(left[0] - right[0], left[1] - right[1]) <= LINK_M:
                parent[find(j)] = find(i)
    groups: dict[int, list[tuple[float, float, float]]] = {}
    for index, point in enumerate(kept):
        groups.setdefault(find(index), []).append(point)
    fitted: list[tuple[float, float, float, float]] = []
    for group in groups.values():
        if len(group) < 3:
            continue
        cx = sum(p[0] for p in group) / len(group)
        cy = sum(p[1] for p in group) / len(group)
        sxx = syy = sxy = 0.0
        for x, y, _z in group:
            dx = x - cx
            dy = y - cy
            sxx += dx * dx
            syy += dy * dy
            sxy += dx * dy
        if abs(sxy) < 1e-12 and sxx >= syy:
            ax, ay = 1.0, 0.0
        elif abs(sxy) < 1e-12:
            ax, ay = 0.0, 1.0
        else:
            trace = sxx + syy
            det = sxx * syy - sxy * sxy
            eigen = trace / 2.0 + math.sqrt(max(0.0, trace * trace / 4.0 - det))
            vx, vy = sxy, eigen - sxx
            norm = math.hypot(vx, vy) or 1.0
            ax, ay = vx / norm, vy / norm
        uv = [((x - cx) * ax + (y - cy) * ay, z) for x, y, z in group]
        result = circle_fit(uv)
        if result is None:
            continue
        diameter, rms = result
        if math.isfinite(diameter) and math.isfinite(rms):
            fitted.append((cx, cy, diameter, rms))
    if not fitted:
        return {
            "word": "missing",
            "points": len(kept),
            "dropped": dropped,
            "width": None,
            "length": None,
            "sections": 0,
            "rms": None,
        }
    order = sorted(fitted, key=lambda item: (item[0], item[1]))
    chain = [order[0]]
    rest = order[1:]
    while rest:
        x0, y0 = chain[-1][0], chain[-1][1]
        nxt = min(rest, key=lambda item: math.hypot(item[0] - x0, item[1] - y0))
        chain.append(nxt)
        rest.remove(nxt)
    diameters = sorted(item[2] for item in chain)
    mid = len(diameters) // 2
    if len(diameters) % 2:
        width = diameters[mid]
    else:
        width = (diameters[mid - 1] + diameters[mid]) / 2.0
    length = 0.0
    for left, right in zip(chain, chain[1:]):
        length += math.hypot(right[0] - left[0], right[1] - left[1])
    rms = max(item[3] for item in chain)
    return {
        "word": walk(width, length, "return", False),
        "points": len(kept),
        "dropped": dropped,
        "width": width,
        "length": length,
        "sections": len(fitted),
        "rms": rms,
    }


def section_line(scored: dict[str, float | int | str | None]) -> str:
    def show(value: float | None) -> str:
        if value is None:
            return "missing"
        if abs(value) < 1e-9:
            return "0"
        return f"{value:.10g}"

    return (
        f"{scored['word']} sections={scored['sections']} points={scored['points']} "
        f"dropped={scored['dropped']} width={show(scored['width'])} "
        f"length={show(scored['length'])} rms={show(scored['rms'])} "
        f"echo=return clutter=false"
    )
