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

"""32-bit integer compressor used by a LAZ chunk table.

Two contexts. Context 0 is the point count. Context 1 is the byte size.
The corrector models are shared. Counts start at 1. A value of 109 with
the previous size 0, on context 1, is the five bytes 3c d8 00 00 00.
"""

from __future__ import annotations

import struct

_DM = 15
_BM = 13
_AC_MIN = 0x01000000
_AC_MAX = 0xFFFFFFFF
_BITS = 32
_CONTEXTS = 2
_HIGH = 8


def _u32(value: int) -> int:
    return value & _AC_MAX


def _i32(value: int) -> int:
    value = _u32(value)
    if value >= 0x80000000:
        value -= 0x100000000
    return value


def _sub(real: int, pred: int) -> int:
    return _i32(real - pred)


class _Symbols:
    def __init__(self, symbols: int) -> None:
        self.symbols = symbols
        self.last = symbols - 1
        self.count = [1] * symbols
        self.dist = [0] * symbols
        self.total = 0
        self.until = 0
        self.cycle = symbols
        self._update()
        self.until = self.cycle = (symbols + 6) >> 1

    def _update(self) -> None:
        if (self.total + self.cycle) > (1 << _DM):
            self.total = 0
            for index, count in enumerate(self.count):
                self.count[index] = (count + 1) >> 1
                self.total += self.count[index]
        else:
            self.total += self.cycle
        scale = 0x80000000 // self.total
        running = 0
        for index, count in enumerate(self.count):
            self.dist[index] = (scale * running) >> (31 - _DM)
            running += count
        self.cycle = (5 * self.cycle) >> 2
        cap = (self.symbols + 6) << 3
        if self.cycle > cap:
            self.cycle = cap
        self.until = self.cycle

    def seen(self, sym: int) -> None:
        self.count[sym] += 1
        self.until -= 1
        if self.until == 0:
            self._update()


class _Bit:
    def __init__(self) -> None:
        self.zero_count = 1
        self.count = 2
        self.prob = 1 << (_BM - 1)
        self.until = 4
        self.cycle = 4

    def seen(self, sym: int) -> None:
        if sym == 0:
            self.zero_count += 1
        self.until -= 1
        if self.until == 0:
            self._update()

    def _update(self) -> None:
        if (self.count + self.cycle) > (1 << _BM):
            self.count = (self.count + self.cycle + 1) >> 1
            self.zero_count = (self.zero_count + 1) >> 1
            if self.zero_count == self.count:
                self.count += 1
        else:
            self.count += self.cycle
        scale = 0x80000000 // self.count
        self.prob = (self.zero_count * scale) >> (31 - _BM)
        self.cycle = (5 * self.cycle) >> 2
        if self.cycle > 64:
            self.cycle = 64
        self.until = self.cycle


class _Coder:
    def __init__(self, blob: bytes | None = None) -> None:
        self.base = 0
        self.length = _AC_MAX
        self.out = bytearray()
        self.blob = blob or b""
        self.at = 0
        self.value = 0
        if blob is not None:
            self.value = 0
            for _ in range(4):
                self.value = _u32((self.value << 8) | self._byte())

    def _byte(self) -> int:
        if self.at >= len(self.blob):
            return 0
        byte = self.blob[self.at]
        self.at += 1
        return byte

    def _renorm_enc(self) -> None:
        while self.length < _AC_MIN:
            self.out.append((self.base >> 24) & 0xFF)
            self.base = _u32(self.base << 8)
            self.length = _u32(self.length << 8)

    def _renorm_dec(self) -> None:
        while self.length < _AC_MIN:
            self.value = _u32((self.value << 8) | self._byte())
            self.length = _u32(self.length << 8)

    def _carry(self) -> None:
        index = len(self.out) - 1
        while index >= 0 and self.out[index] == 0xFF:
            self.out[index] = 0
            index -= 1
        if index < 0:
            raise ValueError("bad class")
        self.out[index] = (self.out[index] + 1) & 0xFF

    def encode_symbol(self, model: _Symbols, sym: int) -> None:
        if sym == model.last:
            x = _u32(model.dist[sym] * (self.length >> _DM))
            init = self.base
            self.base = _u32(self.base + x)
            self.length = _u32(self.length - x)
        else:
            self.length >>= _DM
            x = _u32(model.dist[sym] * self.length)
            init = self.base
            self.base = _u32(self.base + x)
            self.length = _u32(model.dist[sym + 1] * self.length - x)
        if init > self.base:
            self._carry()
        if self.length < _AC_MIN:
            self._renorm_enc()
        model.seen(sym)

    def decode_symbol(self, model: _Symbols) -> int:
        sym = 0
        n = model.symbols
        y = self.length
        self.length >>= _DM
        k = n >> 1
        x = 0
        while True:
            z = _u32(self.length * model.dist[k])
            if z > self.value:
                n = k
                y = z
            else:
                sym = k
                x = z
            nxt = (sym + n) >> 1
            if nxt == sym:
                break
            k = nxt
        self.value = _u32(self.value - x)
        self.length = _u32(y - x)
        if self.length < _AC_MIN:
            self._renorm_dec()
        model.seen(sym)
        return sym

    def encode_bit(self, model: _Bit, sym: int) -> None:
        x = _u32(model.prob * (self.length >> _BM))
        if sym == 0:
            self.length = x
        else:
            init = self.base
            self.base = _u32(self.base + x)
            self.length = _u32(self.length - x)
            if init > self.base:
                self._carry()
        if self.length < _AC_MIN:
            self._renorm_enc()
        model.seen(sym)

    def decode_bit(self, model: _Bit) -> int:
        x = _u32(model.prob * (self.length >> _BM))
        sym = 1 if self.value >= x else 0
        if sym == 0:
            self.length = x
        else:
            self.value = _u32(self.value - x)
            self.length = _u32(self.length - x)
        if self.length < _AC_MIN:
            self._renorm_dec()
        model.seen(sym)
        return sym

    def write_bits(self, bits: int, sym: int) -> None:
        if bits > 19:
            self.write_bits(16, sym & 0xFFFF)
            sym >>= 16
            bits -= 16
        init = self.base
        self.length >>= bits
        self.base = _u32(self.base + sym * self.length)
        if init > self.base:
            self._carry()
        if self.length < _AC_MIN:
            self._renorm_enc()

    def read_bits(self, bits: int) -> int:
        if bits > 19:
            low = self.read_bits(16)
            high = self.read_bits(bits - 16)
            return (high << 16) | low
        self.length >>= bits
        sym = self.value // self.length if self.length else 0
        self.value = _u32(self.value - self.length * sym)
        if self.length < _AC_MIN:
            self._renorm_dec()
        return sym

    def finish(self) -> bytes:
        init = self.base
        if self.length > 2 * _AC_MIN:
            self.base = _u32(self.base + _AC_MIN)
            self.length = _AC_MIN >> 1
            extra = True
        else:
            self.base = _u32(self.base + (_AC_MIN >> 1))
            self.length = _AC_MIN >> 9
            extra = False
        if init > self.base:
            self._carry()
        self._renorm_enc()
        self.out.append(0)
        self.out.append(0)
        if extra:
            self.out.append(0)
        return bytes(self.out)


class IntegerCompressor:
    """32-bit, two contexts, high bits 8. The same pair the chunk table uses."""

    def __init__(self, coder: _Coder) -> None:
        self.coder = coder
        self.k_model = [_Symbols(_BITS + 1) for _ in range(_CONTEXTS)]
        self.corrector: list[_Symbols | _Bit] = [_Bit()]
        for k in range(1, _BITS + 1):
            width = 1 << k if k <= _HIGH else 1 << _HIGH
            self.corrector.append(_Symbols(width))

    def compress(self, pred: int, real: int, context: int) -> None:
        corr = _sub(real, pred)
        c1 = -corr if corr <= 0 else corr - 1
        k = 0
        while c1:
            c1 >>= 1
            k += 1
        self.coder.encode_symbol(self.k_model[context], k)
        if k == 0:
            bit = self.corrector[0]
            assert isinstance(bit, _Bit)
            self.coder.encode_bit(bit, corr)
            return
        if k >= 32:
            return
        c = corr + ((1 << k) - 1) if corr < 0 else corr - 1
        if k <= _HIGH:
            model = self.corrector[k]
            assert isinstance(model, _Symbols)
            self.coder.encode_symbol(model, c)
            return
        k1 = k - _HIGH
        low = c & ((1 << k1) - 1)
        high = c >> k1
        model = self.corrector[k]
        assert isinstance(model, _Symbols)
        self.coder.encode_symbol(model, high)
        self.coder.write_bits(k1, low)

    def decompress(self, pred: int, context: int) -> int:
        k = self.coder.decode_symbol(self.k_model[context])
        if k == 0:
            bit = self.corrector[0]
            assert isinstance(bit, _Bit)
            corr = self.coder.decode_bit(bit)
        elif k >= 32:
            corr = -2147483648
        else:
            if k <= _HIGH:
                model = self.corrector[k]
                assert isinstance(model, _Symbols)
                c = self.coder.decode_symbol(model)
            else:
                k1 = k - _HIGH
                model = self.corrector[k]
                assert isinstance(model, _Symbols)
                high = self.coder.decode_symbol(model)
                low = self.coder.read_bits(k1)
                c = (high << k1) | low
            if c >= (1 << (k - 1)):
                corr = c + 1
            else:
                corr = c - ((1 << k) - 1)
        return _i32(pred + corr)


def encode_table(entries: list[tuple[int | None, int]]) -> bytes:
    """Version 0, the chunk count, then the compressed deltas.

    A missing point count means fixed-size chunks: only the byte size is
    stored, on context 1. Context 0 is unused, which is the fixed-size rule.
    """
    coder = _Coder()
    comp = IntegerCompressor(coder)
    prev_count = 0
    prev_size = 0
    for count, size in entries:
        if count is not None:
            comp.compress(prev_count, count, 0)
            prev_count = count
        comp.compress(prev_size, size, 1)
        prev_size = size
    return struct.pack("<II", 0, len(entries)) + coder.finish()


def decode_table(blob: bytes, point_counts: bool) -> list[tuple[int | None, int]]:
    if len(blob) < 8:
        raise ValueError("bad class")
    version, count = struct.unpack_from("<II", blob, 0)
    if version != 0:
        raise ValueError("bad class")
    coder = _Coder(blob[8:])
    comp = IntegerCompressor(coder)
    rows: list[tuple[int | None, int]] = []
    prev_count = 0
    prev_size = 0
    for _ in range(count):
        if point_counts:
            prev_count = comp.decompress(prev_count, 0)
            got: int | None = prev_count
        else:
            got = None
        prev_size = comp.decompress(prev_size, 1)
        rows.append((got, prev_size))
    return rows
