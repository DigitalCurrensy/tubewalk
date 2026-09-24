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

"""LAS 1.4 point classes and the LAZ point-14 classification context.

Class names are Table 17 of LAS 1.4 R15, formats 6 to 10. Class 8 and class 12
are reserved. A key-point and an overlap are flags, not those two numbers.
The context index is the point-14 rule: 256 symbols, 64 instances,
(previous class mod 32) * 2, plus 1 when this return is 1 and the pulse has
fewer than 2 returns. Counts start at 1. This is not LASzip's initial model
and it does not open a .laz file.
"""

from __future__ import annotations

ASPRS_14 = {
    0: "created, never classified",
    1: "unclassified",
    2: "ground",
    3: "low vegetation",
    4: "medium vegetation",
    5: "high vegetation",
    6: "building",
    7: "low point",
    8: "reserved",
    9: "water",
    10: "rail",
    11: "road surface",
    12: "reserved",
    13: "wire guard",
    14: "wire conductor",
    15: "transmission tower",
    16: "wire connector",
    17: "bridge deck",
    18: "high noise",
    19: "overhead structure",
    20: "ignored ground",
    21: "snow",
    22: "temporal exclusion",
}

# Format 6 classification-flag bits. They are not class numbers.
SYNTHETIC = 1
KEY_POINT = 2
WITHHELD = 4
OVERLAP = 8

_MASK = 0xFFFFFFFF
_HALF = 0x80000000
_QUARTER = 0x40000000
SEED = 1


def asprs_name(code: int) -> str:
    if isinstance(code, bool) or not isinstance(code, int) or code < 0 or code > 255:
        raise ValueError("bad class")
    if code in ASPRS_14:
        return ASPRS_14[code]
    if code <= 63:
        return "reserved"
    return "user"


def classification_flags(
    synthetic: bool = False,
    key_point: bool = False,
    withheld: bool = False,
    overlap: bool = False,
) -> int:
    return (
        (SYNTHETIC if synthetic else 0)
        | (KEY_POINT if key_point else 0)
        | (WITHHELD if withheld else 0)
        | (OVERLAP if overlap else 0)
    )


def point14_instance(previous: int, return_number: int, number_of_returns: int) -> int:
    """Index of the symbol model for this point's class. 0 to 63."""
    for value in (previous, return_number, number_of_returns):
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError("bad class")
    if previous < 0 or previous > 255 or return_number < 0 or number_of_returns < 0:
        raise ValueError("bad class")
    single = 1 if return_number == 1 and number_of_returns < 2 else 0
    return (previous % 32) * 2 + single


def encode_point14(points: list[tuple[int, int, int]]) -> bytes:
    """First class is raw. Each later class is a 256-symbol, 64-instance code."""
    if len(points) > 255 or not points:
        raise ValueError("bad class")
    for point in points:
        asprs_name(point[0])
        point14_instance(*point)
    counts = [[SEED] * 256 for _ in range(64)]
    totals = [SEED * 256] * 64
    low = 0
    high = _MASK
    pending = 0
    out = bytearray()

    def emit(bit: int) -> None:
        nonlocal pending
        out.append(bit)
        while pending:
            out.append(bit ^ 1)
            pending -= 1

    def renorm() -> None:
        nonlocal low, high, pending
        while True:
            if high < _HALF:
                emit(0)
            elif low >= _HALF:
                emit(1)
                low -= _HALF
                high -= _HALF
            elif low >= _QUARTER and high < 3 * _QUARTER:
                pending += 1
                low -= _QUARTER
                high -= _QUARTER
            else:
                break
            low = (low << 1) & _MASK
            high = ((high << 1) | 1) & _MASK

    for index, point in enumerate(points):
        if index == 0:
            continue
        symbol = point[0]
        instance = point14_instance(points[index - 1][0], point[1], point[2])
        cum = sum(counts[instance][:symbol])
        freq = counts[instance][symbol]
        total = totals[instance]
        span = high - low + 1
        high = low + (span * (cum + freq) // total) - 1
        low = low + (span * cum // total)
        counts[instance][symbol] += 1
        totals[instance] += 1
        renorm()
    pending += 1
    emit(1 if low >= _QUARTER else 0)
    return bytes([len(points), points[0][0]]) + bytes(out)


def decode_point14(blob: bytes, returns: list[tuple[int, int]]) -> list[int]:
    """`returns` is (return number, number of returns) for every point, including the first."""
    if len(blob) < 2:
        raise ValueError("bad class")
    count = blob[0]
    if count != len(returns) or count == 0:
        raise ValueError("bad class")
    classes = [blob[1]]
    asprs_name(classes[0])
    if count == 1:
        return classes
    packed = list(blob[2:])
    index = 0

    def bit() -> int:
        nonlocal index
        if index >= len(packed):
            return 0
        value = packed[index]
        index += 1
        return value

    counts = [[SEED] * 256 for _ in range(64)]
    totals = [SEED * 256] * 64
    low = 0
    high = _MASK
    code = 0
    for _ in range(32):
        code = ((code << 1) | bit()) & _MASK
    for point_index in range(1, count):
        instance = point14_instance(classes[-1], returns[point_index][0], returns[point_index][1])
        span = high - low + 1
        target = ((code - low + 1) * totals[instance] - 1) // span
        cum = 0
        symbol = 255
        freq = counts[instance][255]
        for guess in range(256):
            freq = counts[instance][guess]
            if cum + freq > target:
                symbol = guess
                break
            cum += freq
        high = low + (span * (cum + freq) // totals[instance]) - 1
        low = low + (span * cum // totals[instance])
        counts[instance][symbol] += 1
        totals[instance] += 1
        while True:
            if high < _HALF:
                pass
            elif low >= _HALF:
                low -= _HALF
                high -= _HALF
                code -= _HALF
            elif low >= _QUARTER and high < 3 * _QUARTER:
                low -= _QUARTER
                high -= _QUARTER
                code -= _QUARTER
            else:
                break
            low = (low << 1) & _MASK
            high = ((high << 1) | 1) & _MASK
            code = ((code << 1) | bit()) & _MASK
        classes.append(symbol)
    return classes


def encode_chunks(chunks: list[list[tuple[int, int, int]]]) -> bytes:
    """Our chunk index. Magic, count, then offset and point count for each chunk.

    This is not the LAZ chunk table. A .laz file still goes through lazrs.
    """
    import struct

    if not chunks or len(chunks) > 65535:
        raise ValueError("bad class")
    payloads = [encode_point14(chunk) for chunk in chunks]
    header = 6 + 6 * len(chunks)
    out = bytearray(b"CHK1")
    out += struct.pack("<H", len(chunks))
    offset = header
    for chunk, payload in zip(chunks, payloads):
        out += struct.pack("<IH", offset, len(chunk))
        offset += len(payload)
    for payload in payloads:
        out += payload
    return bytes(out)


def decode_chunks(blob: bytes, returns: list[list[tuple[int, int]]]) -> list[list[int]]:
    import struct

    if len(blob) < 6 or blob[:4] != b"CHK1":
        raise ValueError("bad class")
    count = struct.unpack_from("<H", blob, 4)[0]
    if count != len(returns):
        raise ValueError("bad class")
    entries: list[tuple[int, int]] = []
    pos = 6
    for _ in range(count):
        if pos + 6 > len(blob):
            raise ValueError("bad class")
        entries.append(struct.unpack_from("<IH", blob, pos))
        pos += 6
    ends = [item[0] for item in entries[1:]] + [len(blob)]
    decoded: list[list[int]] = []
    for (offset, npoints), end, pulse in zip(entries, ends, returns):
        payload = blob[offset:end]
        if not payload or payload[0] != npoints:
            raise ValueError("bad class")
        decoded.append(decode_point14(payload, pulse))
    return decoded


def encode_laz_index(chunks: list[list[tuple[int, int, int]]]) -> bytes:
    """Published chunk-table layout, with the table stored raw.

    Byte 0 is a little-endian int64, the position of the table in this block.
    The table is version 0, then the chunk count, then two signed deltas per
    chunk: point count, then payload bytes. The first delta is the value
    itself because the previous value is 0. Later deltas are this chunk minus
    the previous chunk. LAZ compresses those integers. This file does not.
    """
    import struct

    if not chunks or len(chunks) > 65535:
        raise ValueError("bad class")
    payloads = [encode_point14(chunk) for chunk in chunks]
    table_at = 8 + sum(len(payload) for payload in payloads)
    out = bytearray(struct.pack("<q", table_at))
    for payload in payloads:
        out += payload
    out += struct.pack("<II", 0, len(chunks))
    previous_count = 0
    previous_size = 0
    for chunk, payload in zip(chunks, payloads):
        out += struct.pack("<ii", len(chunk) - previous_count, len(payload) - previous_size)
        previous_count = len(chunk)
        previous_size = len(payload)
    return bytes(out)


def decode_laz_index(blob: bytes, returns: list[list[tuple[int, int]]]) -> list[list[int]]:
    import struct

    if len(blob) < 16:
        raise ValueError("bad class")
    table_at = struct.unpack_from("<q", blob, 0)[0]
    if table_at < 8 or table_at + 8 > len(blob):
        raise ValueError("bad class")
    version, count = struct.unpack_from("<II", blob, table_at)
    if version != 0 or count != len(returns):
        raise ValueError("bad class")
    if table_at + 8 + 8 * count != len(blob):
        raise ValueError("bad class")
    previous_count = 0
    previous_size = 0
    entries: list[tuple[int, int]] = []
    for index in range(count):
        d_count, d_size = struct.unpack_from("<ii", blob, table_at + 8 + 8 * index)
        previous_count += d_count
        previous_size += d_size
        if previous_count <= 0 or previous_size <= 0:
            raise ValueError("bad class")
        entries.append((previous_count, previous_size))
    offset = 8
    decoded: list[list[int]] = []
    for (npoints, size), pulse in zip(entries, returns):
        payload = blob[offset : offset + size]
        offset += size
        if len(payload) != size or payload[0] != npoints:
            raise ValueError("bad class")
        decoded.append(decode_point14(payload, pulse))
    if offset != table_at:
        raise ValueError("bad class")
    return decoded
