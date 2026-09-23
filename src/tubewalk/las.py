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

"""LAS 1.2 point formats 0 and 1. LAZ is compressed and is not read."""

from __future__ import annotations

import struct
from pathlib import Path

# ASPRS LAS 1.2 public header is 227 bytes when there is no extra data.
# Point format 0 is 20 bytes. Point format 1 adds an 8-byte GPS time.
HEADER = 227
RECORD = {0: 20, 1: 28}


def read_las(path: Path) -> list[tuple[float, float, float, int, int]]:
    """Return x, y, z, return number, classification.

    xyz = integer * scale + offset, from the header doubles at bytes 131 and 155.
    The return number is the low 3 bits of byte 14. The class is the low 5 bits
    of byte 15. A file that is not LASF, not version 1.2, or not format 0 or 1
    raises ValueError. Variable-length records are skipped, not interpreted.
    """
    blob = path.read_bytes()
    if len(blob) < HEADER or blob[0:4] != b"LASF":
        raise ValueError("not a las")
    major, minor = blob[24], blob[25]
    if (major, minor) != (1, 2):
        raise ValueError("not las 1.2")
    header_size, offset, _vlr, fmt, record_length, count = struct.unpack_from("<HI I BHI", blob, 94)
    if header_size < HEADER or fmt not in RECORD or record_length < RECORD[fmt]:
        raise ValueError("not this las")
    scale = struct.unpack_from("<3d", blob, 131)
    origin = struct.unpack_from("<3d", blob, 155)
    points: list[tuple[float, float, float, int, int]] = []
    for index in range(count):
        start = offset + index * record_length
        if start + RECORD[fmt] > len(blob):
            raise ValueError("short las")
        x, y, z = struct.unpack_from("<3i", blob, start)
        flags, klass = blob[start + 14], blob[start + 15]
        points.append(
            (
                x * scale[0] + origin[0],
                y * scale[1] + origin[1],
                z * scale[2] + origin[2],
                flags & 0b111,
                klass & 0b11111,
            )
        )
    return points


def read_laz(path: Path) -> list[tuple[float, float, float, int, int]]:
    """Read a LAZ file. The bytes are LASzip, not this module's codec.

    LASzip predicts each point from earlier points and compresses the
    leftovers with a range coder, in chunks, so a reader can seek. lazrs
    is the decoder. A missing decoder raises ValueError. The values returned
    are the same five numbers read_las returns.
    """
    try:
        import laspy
    except ImportError as exc:
        raise ValueError("laz needs lazrs") from exc
    try:
        cloud = laspy.read(str(path))
    except Exception as exc:
        raise ValueError("not a laz") from exc
    returns = cloud.return_number
    classes = cloud.classification
    points: list[tuple[float, float, float, int, int]] = []
    for index in range(len(cloud.points)):
        points.append(
            (
                float(cloud.x[index]),
                float(cloud.y[index]),
                float(cloud.z[index]),
                int(returns[index]) & 0b111,
                int(classes[index]) & 0b11111,
            )
        )
    return points
