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
import sys
from pathlib import Path

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
    return float(text)


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
    raise ValueError(f"not a boolean: {text}")


def score_row(row: dict[str, str | None]) -> str:
    return walk(
        _optional_float(_cell(row, "width_m")),
        _optional_float(_cell(row, "length_m")),
        _optional_text(_cell(row, "echo")),
        _bool(_cell(row, "clutter")),
    )


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        print("usage: python -m tubewalk <csv>", file=sys.stderr)
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
            print(score_row(row))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
