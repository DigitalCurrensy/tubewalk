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

"""Print one walk() verdict per conduit row. Empty numbers are missing."""

from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

from .cloth import cloth_line
from .las import read_las
from .lidar import cloud_line, reduce_cloud
from .section import section_line, section_score
from .tube import walk

COLUMNS = ("width_m", "length_m", "echo", "clutter")


def _cell(row: dict[str, str | None], name: str) -> str:
    value = row.get(name)
    if value is None:
        return ""
    return value.strip()


def _optional_float(text: str) -> float | None:
    if text == "":
        return None
    try:
        return float(text)
    except ValueError:
        return float("nan")


def _optional_text(text: str) -> str | None:
    if text == "":
        return None
    return text


def _bool(text: str) -> bool:
    if text == "":
        return False
    lowered = text.casefold()
    if lowered in {"true", "yes", "y", "1"}:
        return True
    if lowered in {"false", "no", "n", "0"}:
        return False
    return None



def _show(value: float | None) -> str:
    if value is None:
        return "missing"
    if not math.isfinite(value):
        return "bad"
    return f"{value:.10g}"


def score_row(row: dict[str, str | None]) -> str:
    clutter = _bool(_cell(row, "clutter"))
    if clutter is None:
        return "missing"
    return walk(
        _optional_float(_cell(row, "width_m")),
        _optional_float(_cell(row, "length_m")),
        _optional_text(_cell(row, "echo")),
        clutter,
    )


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) == 2 and args[0] == "lidar":
        return _lidar(Path(args[1]))
    if len(args) == 2 and args[0] == "cloth":
        return _print_points(Path(args[1]), "cloth")
    if len(args) == 2 and args[0] == "section":
        return _print_points(Path(args[1]), "section")
    if len(args) == 2 and args[0] == "las":
        return _las(Path(args[1]))
    if len(args) != 1:
        print(
            "usage: python -m tubewalk <csv> | lidar <cloud.csv> | cloth <cloud.csv> | section <cloud.csv> | las <file.las>",
            file=sys.stderr,
        )
        return 2
    path = Path(args[0])
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        names = [name.strip() for name in (reader.fieldnames or [])]
        if names != list(COLUMNS):
            print(
                "csv columns must be width_m,length_m,echo,clutter",
                file=sys.stderr,
            )
            return 2
        for row in reader:
            if all(not (value or "").strip() for value in row.values()):
                continue
            width = _optional_float(_cell(row, "width_m"))
            length = _optional_float(_cell(row, "length_m"))
            echo = _optional_text(_cell(row, "echo"))
            clutter = _bool(_cell(row, "clutter"))
            echo_text = "missing" if echo is None else echo
            if clutter is None:
                print(
                    f"missing width={_show(width)} length={_show(length)} "
                    f"echo={echo_text} clutter=bad"
                )
                continue
            word = walk(width, length, echo, clutter)
            print(
                f"{word} width={_show(width)} length={_show(length)} "
                f"echo={echo_text} clutter={'true' if clutter else 'false'}"
            )
    return 0


def _lidar(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        names = [name.strip() for name in (reader.fieldnames or [])]
        if names not in (["x", "y", "z"], ["x", "y", "z", "return"], ["x", "y", "z", "return", "class"]):
            print("csv columns must be x,y,z or x,y,z,return,class", file=sys.stderr)
            return 2
        rows = [{key.strip(): value for key, value in row.items() if key} for row in reader]
    print(cloud_line(reduce_cloud(rows)))
    return 0


def _rows(path: Path) -> list[tuple[float, float, float]] | None:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        names = [name.strip() for name in (reader.fieldnames or [])]
        if names[:3] != ["x", "y", "z"]:
            print("csv columns must start with x,y,z", file=sys.stderr)
            return None
        points = []
        for row in reader:
            if all(not (value or "").strip() for value in row.values()):
                continue
            try:
                points.append((float(row["x"]), float(row["y"]), float(row["z"])))
            except (TypeError, ValueError):
                points.append((float("nan"), float("nan"), float("nan")))
        return points


def _print_points(path: Path, kind: str) -> int:
    points = _rows(path)
    if points is None:
        return 2
    if kind == "cloth":
        print(cloth_line(points))
    else:
        print(section_line(section_score(points)))
    return 0


def _las(path: Path) -> int:
    try:
        raw = read_las(path)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2
    kept = [(x, y, z) for x, y, z, _ret, klass in raw if klass != 7]
    print(section_line(section_score(kept)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
