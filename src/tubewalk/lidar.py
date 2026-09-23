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

"""Span of a point list. X is length. Y is width. Not a classified cloud."""

from __future__ import annotations

import math

from .tube import walk

# ASPRS LAS class 7 is low-point noise. Those points are not part of the span.
NOISE_CLASS = 7


def _number(text: str) -> float | None:
    if text.strip() == "":
        return None
    try:
        value = float(text)
    except ValueError:
        return None
    if not math.isfinite(value):
        return None
    return value


def reduce_cloud(rows: list[dict[str, str | None]]) -> dict[str, float | int | str | bool | None]:
    """Keep finite returns that are not class 7. Span the rest.

    Length is max(x) - min(x). Width is max(y) - min(y). The caller already
    aligned the tube with X. A secondary return, return number greater than 1,
    sets clutter. No return column means clutter is false. Fewer than two
    kept points is missing. This is not a ground filter, a centerline, or a
    fitted cylinder.
    """
    kept_x: list[float] = []
    kept_y: list[float] = []
    dropped = 0
    secondary = 0
    saw_return = False
    for row in rows:
        if all(not (value or "").strip() for value in row.values()):
            continue
        x = _number(str(row.get("x") or ""))
        y = _number(str(row.get("y") or ""))
        z = _number(str(row.get("z") or ""))
        if x is None or y is None or z is None:
            dropped += 1
            continue
        class_text = str(row.get("class") or "").strip()
        if class_text != "":
            klass = _number(class_text)
            if klass is None or klass != int(klass):
                dropped += 1
                continue
            if int(klass) == NOISE_CLASS:
                dropped += 1
                continue
        return_text = str(row.get("return") or "").strip()
        if return_text != "":
            number = _number(return_text)
            if number is None or number != int(number) or number < 1:
                dropped += 1
                continue
            saw_return = True
            if int(number) > 1:
                secondary += 1
        kept_x.append(x)
        kept_y.append(y)
    points = len(kept_x)
    if points < 2:
        return {
            "word": "missing",
            "points": points,
            "dropped": dropped,
            "width": None,
            "length": None,
            "echo": "missing",
            "clutter": False,
        }
    width = max(kept_y) - min(kept_y)
    length = max(kept_x) - min(kept_x)
    clutter = saw_return and secondary > 0
    return {
        "word": walk(width, length, "return", clutter),
        "points": points,
        "dropped": dropped,
        "width": width,
        "length": length,
        "echo": "return",
        "clutter": clutter,
    }


def cloud_line(scored: dict[str, float | int | str | bool | None]) -> str:
    def show(value: float | None) -> str:
        if value is None:
            return "missing"
        return f"{value:.10g}"

    clutter = "true" if scored["clutter"] else "false"
    return (
        f"{scored['word']} points={scored['points']} dropped={scored['dropped']} "
        f"width={show(scored['width'])} length={show(scored['length'])} "
        f"echo={scored['echo']} clutter={clutter}"
    )
