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

"""LAS 1.2 formats 0 and 1, and LAS 1.4 formats 6 and 7. LAZ is separate."""

from __future__ import annotations

import struct
from pathlib import Path

# ASPRS LAS 1.2 public header is 227 bytes. LAS 1.4 is 375 bytes.
# Format 0 is 20 bytes. Format 1 adds GPS time. Format 6 is 30 bytes.
# Format 7 adds three color shorts. The 1.4 point count is the uint64 at byte 247.
HEADER_12 = 227
HEADER_14 = 375
RECORD = {0: 20, 1: 28, 6: 30, 7: 36}


def read_las(path: Path) -> list[tuple[float, float, float, int, int]]:
    """Return x, y, z, return number, classification.

    xyz = integer * scale + offset, from the header doubles at bytes 131 and 155.
    Version 1.2, formats 0 and 1: the return number is the low 3 bits of byte 14
    and the class is the low 5 bits of byte 15.
    Version 1.4, formats 6 and 7: the return number is the low 4 bits of the
    uint16 at byte 14, and the class is the whole byte at offset 16.
    The 1.4 count is the uint64 at byte 247. A file outside those two versions
    raises ValueError. Variable-length records are skipped, not interpreted.
    """
    blob = path.read_bytes()
    if len(blob) < HEADER_12 or blob[0:4] != b"LASF":
        raise ValueError("not a las")
    major, minor = blob[24], blob[25]
    header_size, offset, _vlr, fmt, record_length, legacy = struct.unpack_from("<HIIBHI", blob, 94)
    if (major, minor) == (1, 2):
        if header_size < HEADER_12 or fmt not in (0, 1) or record_length < RECORD[fmt]:
            raise ValueError("not this las")
        count = legacy
        modern = False
    elif (major, minor) == (1, 4):
        if header_size < HEADER_14 or len(blob) < HEADER_14 or fmt not in (6, 7):
            raise ValueError("not this las")
        if record_length < RECORD[fmt]:
            raise ValueError("not this las")
        count = struct.unpack_from("<Q", blob, 247)[0]
        modern = True
    else:
        raise ValueError("not las 1.2 or 1.4")
    scale = struct.unpack_from("<3d", blob, 131)
    origin = struct.unpack_from("<3d", blob, 155)
    points: list[tuple[float, float, float, int, int]] = []
    width = RECORD[fmt]
    for index in range(count):
        start = offset + index * record_length
        if start + width > len(blob):
            raise ValueError("short las")
        x, y, z = struct.unpack_from("<3i", blob, start)
        if modern:
            flags = struct.unpack_from("<H", blob, start + 14)[0]
            ret = flags & 0b1111
            klass = blob[start + 16]
        else:
            ret = blob[start + 14] & 0b111
            klass = blob[start + 15] & 0b11111
        points.append(
            (
                x * scale[0] + origin[0],
                y * scale[1] + origin[1],
                z * scale[2] + origin[2],
                ret,
                klass,
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
