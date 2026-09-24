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

"""LAS 1.2 formats 0 to 3, and LAS 1.4 formats 0 to 10. LAZ points are separate."""

from __future__ import annotations

import struct
from pathlib import Path

# ASPRS LAS 1.2 public header is 227 bytes. LAS 1.4 is 375 bytes.
# Minimum point-record lengths are LAS 1.4 R15. A longer record is extra
# bytes or a waveform packet. Those bytes are not read.
# Formats 0-5 keep the legacy record: return is 3 bits, class is 5 bits.
# Formats 6-10 are the point-14 record: return is 4 bits, class is a byte.
LEGACY = {0: 20, 1: 28, 2: 26, 3: 34, 4: 57, 5: 63}
POINT14 = {6: 30, 7: 36, 8: 38, 9: 59, 10: 67}
RECORD = {**LEGACY, **POINT14}
HEADER_12 = 227
HEADER_14 = 375


def read_las(path: Path) -> list[tuple[float, float, float, int, int]]:
    """Return x, y, z, return number, classification.

    xyz = integer * scale + offset, from the header doubles at bytes 131 and 155.
    Version 1.2 accepts formats 0, 1, 2, and 3. Version 1.4 accepts formats
    0 through 10. Formats 0 to 5: the return number is the low 3 bits of
    byte 14 and the class is the low 5 bits of byte 15. Formats 6 to 10:
    the return number is the low 4 bits of the uint16 at byte 14, and the
    class is the whole byte at offset 16. The 1.4 count is the uint64 at
    byte 247. A file outside those two versions raises ValueError.
    A waveform packet, RGB, and NIR are not read. Variable-length records
    are skipped, not interpreted.
    """
    blob = path.read_bytes()
    if len(blob) < HEADER_12 or blob[0:4] != b"LASF":
        raise ValueError("not a las")
    major, minor = blob[24], blob[25]
    header_size, offset, _vlr, fmt, record_length, legacy = struct.unpack_from("<HIIBHI", blob, 94)
    if (major, minor) == (1, 2):
        if header_size < HEADER_12 or fmt not in (0, 1, 2, 3) or record_length < RECORD[fmt]:
            raise ValueError("not this las")
        count = legacy
        point14 = False
    elif (major, minor) == (1, 4):
        if header_size < HEADER_14 or len(blob) < HEADER_14 or fmt not in RECORD:
            raise ValueError("not this las")
        if record_length < RECORD[fmt]:
            raise ValueError("not this las")
        count = struct.unpack_from("<Q", blob, 247)[0]
        point14 = fmt >= 6
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
        if point14:
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


def read_chunk_table(path: Path) -> list[tuple[int, int]]:
    """Point count and compressed size of each chunk, from the file's own table.

    The int64 at the start of the point block is the file position of the table.
    The table is version 0, the chunk count, then the integer compressor.
    A chunk size of 0 or 4294967295 means the counts are in the table.
    Any other chunk size is fixed: the table stores only byte sizes, and each
    count is that size. The last chunk of a fixed file can hold fewer points
    than that. This does not decode the points.
    """
    from tubewalk.integer import decode_table

    blob = path.read_bytes()
    if len(blob) < HEADER_14 or blob[0:4] != b"LASF":
        raise ValueError("not a laz")
    header_size, offset, nvlr = struct.unpack_from("<HII", blob, 94)
    record = None
    pos = header_size
    for _ in range(nvlr):
        if pos + 54 > len(blob):
            raise ValueError("not a laz")
        user = blob[pos + 2 : pos + 18]
        rec_id, rec_len = struct.unpack_from("<HH", blob, pos + 18)
        data = blob[pos + 54 : pos + 54 + rec_len]
        if user.startswith(b"laszip encoded") and rec_id == 22204:
            record = data
        pos += 54 + rec_len
    if record is None or len(record) < 16 or offset + 8 > len(blob):
        raise ValueError("not a laz")
    chunk_size = struct.unpack_from("<I", record, 12)[0]
    table_at = struct.unpack_from("<q", blob, offset)[0]
    if table_at < 0 or table_at >= len(blob):
        raise ValueError("not a laz")
    adaptive = chunk_size in (0, 0xFFFFFFFF)
    rows = decode_table(blob[table_at:], point_counts=adaptive)
    if adaptive:
        return [(int(count), size) for count, size in rows if count is not None]
    return [(chunk_size, size) for _count, size in rows]


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
    fmt = int(cloud.header.point_format.id)
    ret_mask = 0b1111 if fmt >= 6 else 0b111
    cls_mask = 0xFF if fmt >= 6 else 0b11111
    points: list[tuple[float, float, float, int, int]] = []
    for index in range(len(cloud.points)):
        points.append(
            (
                float(cloud.x[index]),
                float(cloud.y[index]),
                float(cloud.z[index]),
                int(returns[index]) & ret_mask,
                int(classes[index]) & cls_mask,
            )
        )
    return points
