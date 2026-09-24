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

"""A range coder for signed deltas. This is not LASzip."""

from __future__ import annotations

# Uniform 256-symbol model. low and high are a 32-bit window.
# A symbol occupies 1/256 of the window. The window is doubled whenever it
# sits in one half, and a follow bit is saved when it sits in the middle.

TOTAL = 256
MASK = 0xFFFFFFFF
HALF = 0x80000000
QUARTER = 0x40000000


def _bytes_of(symbols: list[int]) -> bytes:
    low = 0
    high = MASK
    pending = 0
    out = bytearray()

    def emit(bit: int) -> None:
        nonlocal pending
        out.append(bit)
        while pending:
            out.append(bit ^ 1)
            pending -= 1

    for symbol in symbols:
        if symbol < 0 or symbol > 255:
            raise ValueError("bad symbol")
        span = high - low + 1
        high = low + (span * (symbol + 1) // TOTAL) - 1
        low = low + (span * symbol // TOTAL)
        while True:
            if high < HALF:
                emit(0)
            elif low >= HALF:
                emit(1)
                low -= HALF
                high -= HALF
            elif low >= QUARTER and high < 3 * QUARTER:
                pending += 1
                low -= QUARTER
                high -= QUARTER
            else:
                break
            low = (low << 1) & MASK
            high = ((high << 1) | 1) & MASK
    pending += 1
    emit(1 if low >= QUARTER else 0)
    return bytes(out)


def _symbols_of(blob: bytes, count: int) -> list[int]:
    bits = list(blob)
    index = 0

    def bit() -> int:
        nonlocal index
        if index >= len(bits):
            return 0
        value = bits[index]
        index += 1
        return value

    low = 0
    high = MASK
    code = 0
    for _ in range(32):
        code = ((code << 1) | bit()) & MASK
    symbols = []
    for _ in range(count):
        span = high - low + 1
        value = ((code - low + 1) * TOTAL - 1) // span
        symbols.append(value)
        high = low + (span * (value + 1) // TOTAL) - 1
        low = low + (span * value // TOTAL)
        while True:
            if high < HALF:
                pass
            elif low >= HALF:
                low -= HALF
                high -= HALF
                code -= HALF
            elif low >= QUARTER and high < 3 * QUARTER:
                low -= QUARTER
                high -= QUARTER
                code -= QUARTER
            else:
                break
            low = (low << 1) & MASK
            high = ((high << 1) | 1) & MASK
            code = ((code << 1) | bit()) & MASK
    return symbols


def zigzag(value: int) -> int:
    return (value << 1) ^ (value >> 63)


def unzigzag(value: int) -> int:
    return (value >> 1) ^ -(value & 1)


def encode_deltas(values: list[int]) -> bytes:
    """Range-code zigzag integers. Each integer is one to five bytes."""
    symbols: list[int] = []
    for value in values:
        number = zigzag(value)
        while True:
            piece = number & 0x7F
            number >>= 7
            if number:
                symbols.append(piece | 0x80)
            else:
                symbols.append(piece)
                break
    return bytes([len(symbols)]) + _bytes_of(symbols) if len(symbols) < 256 else _pack(symbols)


def _pack(symbols: list[int]) -> bytes:
    count = len(symbols).to_bytes(4, "little")
    return b"\xff" + count + _bytes_of(symbols)


def decode_deltas(blob: bytes) -> list[int]:
    if not blob:
        raise ValueError("bad range")
    if blob[0] == 255:
        if len(blob) < 5:
            raise ValueError("bad range")
        count = int.from_bytes(blob[1:5], "little")
        symbols = _symbols_of(blob[5:], count)
    else:
        count = blob[0]
        symbols = _symbols_of(blob[1:], count)
    values = []
    number = 0
    shift = 0
    for symbol in symbols:
        number |= (symbol & 0x7F) << shift
        if symbol & 0x80:
            shift += 7
        else:
            values.append(unzigzag(number))
            number = 0
            shift = 0
    if shift:
        raise ValueError("bad range")
    return values


def encode_context(symbols: list[int]) -> bytes:
    """Order-1 range code. The context is the previous byte's high 3 bits.

    Eight models, each a count of 256 symbols starting at 1. LASzip does this
    per bit, and the context there is the magnitude class of the previous
    residual. This is that idea on whole bytes. It does not decode a .laz file.
    """
    if len(symbols) > 255:
        raise ValueError("bad symbol")
    for symbol in symbols:
        if symbol < 0 or symbol > 255:
            raise ValueError("bad symbol")
    counts = [[1] * 256 for _ in range(8)]
    totals = [256] * 8
    low = 0
    high = MASK
    pending = 0
    out = bytearray()
    context = 0

    def emit(bit: int) -> None:
        nonlocal pending
        out.append(bit)
        while pending:
            out.append(bit ^ 1)
            pending -= 1

    for symbol in symbols:
        cum = sum(counts[context][:symbol])
        freq = counts[context][symbol]
        total = totals[context]
        span = high - low + 1
        high = low + (span * (cum + freq) // total) - 1
        low = low + (span * cum // total)
        counts[context][symbol] += 1
        totals[context] += 1
        while True:
            if high < HALF:
                emit(0)
            elif low >= HALF:
                emit(1)
                low -= HALF
                high -= HALF
            elif low >= QUARTER and high < 3 * QUARTER:
                pending += 1
                low -= QUARTER
                high -= QUARTER
            else:
                break
            low = (low << 1) & MASK
            high = ((high << 1) | 1) & MASK
        context = symbol >> 5
    pending += 1
    emit(1 if low >= QUARTER else 0)
    return bytes([len(symbols)]) + bytes(out)


def decode_context(blob: bytes) -> list[int]:
    if not blob:
        raise ValueError("bad range")
    count = blob[0]
    bits = list(blob[1:])
    index = 0

    def bit() -> int:
        nonlocal index
        if index >= len(bits):
            return 0
        value = bits[index]
        index += 1
        return value

    counts = [[1] * 256 for _ in range(8)]
    totals = [256] * 8
    low = 0
    high = MASK
    code = 0
    for _ in range(32):
        code = ((code << 1) | bit()) & MASK
    symbols = []
    context = 0
    for _ in range(count):
        span = high - low + 1
        target = ((code - low + 1) * totals[context] - 1) // span
        cum = 0
        symbol = 255
        freq = counts[context][255]
        for guess in range(256):
            freq = counts[context][guess]
            if cum + freq > target:
                symbol = guess
                break
            cum += freq
        high = low + (span * (cum + freq) // totals[context]) - 1
        low = low + (span * cum // totals[context])
        counts[context][symbol] += 1
        totals[context] += 1
        while True:
            if high < HALF:
                pass
            elif low >= HALF:
                low -= HALF
                high -= HALF
                code -= HALF
            elif low >= QUARTER and high < 3 * QUARTER:
                low -= QUARTER
                high -= QUARTER
                code -= QUARTER
            else:
                break
            low = (low << 1) & MASK
            high = ((high << 1) | 1) & MASK
            code = ((code << 1) | bit()) & MASK
        symbols.append(symbol)
        context = symbol >> 5
    return symbols


def encode_bits(values: list[int]) -> bytes:
    """Per-bit range code. The context is the previous residual's magnitude class.

    Class is min(7, bit length). Each bit has its own zero-count and one-count,
    starting at 1. A value is a zero flag, five length bits, a sign, then the
    magnitude bits below the leading 1. LASzip uses this family on the bits of
    a predicted residual. This function does not decode a .laz file.
    """
    if len(values) > 255:
        raise ValueError("bad symbol")
    zeros = [1] * (8 * 40)
    ones = [1] * (8 * 40)
    low = 0
    high = MASK
    pending = 0
    out = bytearray()
    previous = 0

    def emit(bit: int) -> None:
        nonlocal pending
        out.append(bit)
        while pending:
            out.append(bit ^ 1)
            pending -= 1

    def renorm() -> None:
        nonlocal low, high, pending
        while True:
            if high < HALF:
                emit(0)
            elif low >= HALF:
                emit(1)
                low -= HALF
                high -= HALF
            elif low >= QUARTER and high < 3 * QUARTER:
                pending += 1
                low -= QUARTER
                high -= QUARTER
            else:
                break
            low = (low << 1) & MASK
            high = ((high << 1) | 1) & MASK

    def put(bit: int, slot: int) -> None:
        nonlocal low, high
        context = previous * 40 + slot
        total = zeros[context] + ones[context]
        span = high - low + 1
        split = low + (span * zeros[context] // total)
        if bit == 0:
            high = split - 1
            zeros[context] += 1
        else:
            low = split
            ones[context] += 1
        if low > high:
            raise ValueError("bad range")
        renorm()

    for value in values:
        if isinstance(value, bool) or not isinstance(value, int) or abs(value) > 2**30:
            raise ValueError("bad symbol")
        magnitude = abs(value)
        length = magnitude.bit_length()
        if length == 0:
            put(0, 0)
            previous = 0
            continue
        put(1, 0)
        for shift in range(5):
            put((length >> shift) & 1, 1 + shift)
        put(1 if value < 0 else 0, 6)
        for shift in range(length - 1):
            put((magnitude >> shift) & 1, 7 + shift)
        previous = min(7, length)
    pending += 1
    emit(1 if low >= QUARTER else 0)
    return bytes([len(values)]) + bytes(out)


def decode_bits(blob: bytes) -> list[int]:
    if not blob:
        raise ValueError("bad range")
    count = blob[0]
    packed = list(blob[1:])
    index = 0

    def next_bit() -> int:
        nonlocal index
        if index >= len(packed):
            return 0
        value = packed[index]
        index += 1
        return value

    zeros = [1] * (8 * 40)
    ones = [1] * (8 * 40)
    low = 0
    high = MASK
    code = 0
    for _ in range(32):
        code = ((code << 1) | next_bit()) & MASK
    previous = 0

    def renorm() -> None:
        nonlocal low, high, code
        while True:
            if high < HALF:
                pass
            elif low >= HALF:
                low -= HALF
                high -= HALF
                code -= HALF
            elif low >= QUARTER and high < 3 * QUARTER:
                low -= QUARTER
                high -= QUARTER
                code -= QUARTER
            else:
                break
            low = (low << 1) & MASK
            high = ((high << 1) | 1) & MASK
            code = ((code << 1) | next_bit()) & MASK

    def take(slot: int) -> int:
        nonlocal low, high
        context = previous * 40 + slot
        total = zeros[context] + ones[context]
        span = high - low + 1
        split = low + (span * zeros[context] // total)
        if code < split:
            high = split - 1
            zeros[context] += 1
            bit = 0
        else:
            low = split
            ones[context] += 1
            bit = 1
        renorm()
        return bit

    values = []
    for _ in range(count):
        if take(0) == 0:
            values.append(0)
            previous = 0
            continue
        length = 0
        for shift in range(5):
            length |= take(1 + shift) << shift
        if length == 0 or length > 31:
            raise ValueError("bad range")
        sign = take(6)
        magnitude = 1 << (length - 1)
        for shift in range(length - 1):
            if take(7 + shift):
                magnitude |= 1 << shift
        values.append(-magnitude if sign else magnitude)
        previous = min(7, length)
    return values

