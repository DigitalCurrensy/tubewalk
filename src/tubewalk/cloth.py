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

"""Cloth filter. The ground is what the cloth rests on. A spike is not ground."""

from __future__ import annotations

import math

# Zhang et al., Remote Sensing 2016. The cloud is turned over. A grid falls
# onto it. Verlet step: pos = pos + (pos - old) * (1 - damping) + gravity * dt^2.
# A particle that passes the cell height sticks and stops. Neighbors then pull
# a free particle in height only. The slope pass then accepts a point that
# the cloth left out when it is within one cell of a ground point and within
# SMOOTH meters of that point's height.

DAMPING = 0.01
GRAVITY = 0.2
TIME_STEP2 = 0.65 * 0.65
THRESHOLD = 0.5
SMOOTH = 1.0


def _cell(x: float, y: float, origin_x: float, origin_y: float, step: float, nx: int, ny: int) -> int | None:
    i = int((x - origin_x) / step)
    j = int((y - origin_y) / step)
    if i < 0 or j < 0 or i >= nx or j >= ny:
        return None
    return j * nx + i


def cloth_mask(
    points: list[tuple[float, float, float]],
    resolution: float = 1.0,
    iterations: int = 200,
    rigidness: int = 3,
    threshold: float = THRESHOLD,
) -> list[bool]:
    """True where the inverted point sits within `threshold` of the cloth.

    `resolution` is the cloth spacing in the same units as x and y.
    `rigidness` is how many neighbor-height passes run after each fall.
    A non-finite point is not ground. An empty cloud is an empty mask.
    """
    if resolution <= 0 or not math.isfinite(resolution):
        raise ValueError("bad resolution")
    finite = [p for p in points if all(math.isfinite(v) for v in p)]
    if not finite:
        return [False] * len(points)
    z_max = max(p[2] for p in finite)
    inverted = [(p[0], p[1], z_max - p[2]) for p in finite]
    min_x = min(p[0] for p in inverted)
    min_y = min(p[1] for p in inverted)
    max_x = max(p[0] for p in inverted)
    max_y = max(p[1] for p in inverted)
    nx = max(1, int((max_x - min_x) / resolution) + 1)
    ny = max(1, int((max_y - min_y) / resolution) + 1)
    if nx * ny > 20000:
        raise ValueError("cloth too fine")
    height = [-math.inf] * (nx * ny)
    for x, y, h in inverted:
        index = _cell(x, y, min_x, min_y, resolution, nx, ny)
        if index is not None and h > height[index]:
            height[index] = h
    peak = max(height)
    pos = [peak] * (nx * ny)
    old = [peak] * (nx * ny)
    stuck = [False] * (nx * ny)
    neighbors: list[list[int]] = [[] for _ in range(nx * ny)]
    for j in range(ny):
        for i in range(nx):
            here = j * nx + i
            if i + 1 < nx:
                neighbors[here].append(here + 1)
                neighbors[here + 1].append(here)
            if j + 1 < ny:
                neighbors[here].append(here + nx)
                neighbors[here + nx].append(here)
    for _ in range(iterations):
        for index in range(nx * ny):
            if stuck[index]:
                continue
            previous = pos[index]
            pos[index] = pos[index] + (pos[index] - old[index]) * (1.0 - DAMPING) - GRAVITY * TIME_STEP2
            old[index] = previous
        for index in range(nx * ny):
            if stuck[index] or height[index] == -math.inf:
                continue
            if pos[index] < height[index]:
                pos[index] = height[index]
                stuck[index] = True
        for _pass in range(max(1, rigidness)):
            for index in range(nx * ny):
                for other in neighbors[index]:
                    if index > other:
                        continue
                    delta = pos[other] - pos[index]
                    if stuck[index] and stuck[other]:
                        continue
                    if not stuck[index] and not stuck[other]:
                        pos[index] += delta * 0.5
                        pos[other] -= delta * 0.5
                    elif not stuck[index]:
                        pos[index] += delta
                    else:
                        pos[other] -= delta
    mask: list[bool] = []
    finite_index = 0
    for point in points:
        if not all(math.isfinite(v) for v in point):
            mask.append(False)
            continue
        x, y, _z = finite[finite_index]
        h = inverted[finite_index][2]
        finite_index += 1
        index = _cell(x, y, min_x, min_y, resolution, nx, ny)
        cloth = pos[index] if index is not None else peak
        mask.append(abs(cloth - h) < threshold)
    return _slope(points, mask, resolution)


def _slope(points: list[tuple[float, float, float]], mask: list[bool], cell: float) -> list[bool]:
    """Connect a steep point to a ground neighbor. The spike is too tall."""
    guard = 0
    changed = True
    while changed and guard <= len(points):
        guard += 1
        changed = False
        for index, point in enumerate(points):
            if mask[index] or not all(math.isfinite(value) for value in point):
                continue
            for other, neighbor in enumerate(points):
                if not mask[other]:
                    continue
                flat = math.hypot(point[0] - neighbor[0], point[1] - neighbor[1])
                if flat <= cell * math.sqrt(2.0) + 1e-9 and abs(point[2] - neighbor[2]) <= SMOOTH:
                    mask[index] = True
                    changed = True
                    break
    return mask


def classify(points: list[tuple[float, float, float]], resolution: float = 1.0) -> list[int]:
    """LAS 1.4 classes this pass can assign. 2 ground, 7 low point, 18 high noise, 1 the rest.

    Low and high use the cloth threshold against the median height within one
    cell. That 0.5 m is this file's threshold, not a height in the ASPRS table.
    Vegetation, buildings, water, and rail are not labeled.
    """
    mask = cloth_mask(points, resolution=resolution)
    classes: list[int] = []
    reach = resolution * math.sqrt(2.0) + 1e-9
    for index, point in enumerate(points):
        if not all(math.isfinite(value) for value in point):
            classes.append(0)
            continue
        nearby = [
            other[2]
            for other_index, other in enumerate(points)
            if other_index != index
            and all(math.isfinite(value) for value in other)
            and math.hypot(point[0] - other[0], point[1] - other[1]) <= reach
        ]
        if nearby:
            nearby.sort()
            median = nearby[len(nearby) // 2]
            if point[2] < median - THRESHOLD:
                classes.append(7)
                continue
            if point[2] > median + THRESHOLD:
                classes.append(18)
                continue
        classes.append(2 if mask[index] else 1)
    return classes


def cloth_line(points: list[tuple[float, float, float]], resolution: float = 1.0) -> str:
    classes = classify(points, resolution)
    ground = sum(1 for value in classes if value == 2)
    low = sum(1 for value in classes if value == 7)
    high = sum(1 for value in classes if value == 18)
    rest = sum(1 for value in classes if value == 1)
    return (
        f"ground={ground} other={len(classes) - ground} class2={ground} class1={rest} "
        f"class7={low} class18={high} resolution={resolution:g} threshold={THRESHOLD:g}"
    )
