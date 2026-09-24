# TUBEWALK

The caller supplies width, length, echo, and clutter.

**Owner:** Digital Currensy Inc.
**Copyright:** 2026 Digital Currensy Inc.
**License:** Apache-2.0. The file named LICENSE is the unmodified Apache text. The copyright notice is in NOTICE and at the top of each source file.

## What it decides

A name for that conduit, or a refusal. ok is not a keep. GRAIL is not this catalog.

## The order inside walk()

`walk(width_m, length_m, echo, clutter)` returns the first hit, in this order:

1. **dark** — `echo` is missing, blank, or the word `none` in any case. `NONE` is dark. A value that is not text is `missing`, not an echo.
2. **missing** — `width_m` is missing or `length_m` is missing. A blank is not a measurement. It is not ok.
3. **missing** — `width_m` is negative or `length_m` is negative. Zero is a number. Width 0 is pinch. Length 0 is pinch first if width is also under 10.
4. **pinch** — `width_m < 10`.
5. **stub** — `length_m < 30`.
6. **clutter** — `clutter` is true.
7. **ok** — none of the above.

The line prints width, length, echo, and clutter next to the word. A missing width is still not a pinch. It is missing. A missing length is still not a stub. It is missing. A negative width or length is missing. A non-finite width or length is missing. A width cell that is not a number prints `bad` and the word is `missing`. A clutter cell that is not true or false prints `clutter=bad` and the word is `missing`. Zero is a number. The line-of-sight fringe is half the wavelength. A non-finite wavelength is not a fringe.

## Point span

`python -m tubewalk lidar examples/cloud.csv` reads `x,y,z`, and optional `return` and `class`. X is the length axis. Y is the width axis. The caller already aligned the tube. Z only proves the point is a real return. Height is not a width.

A non-finite coordinate is dropped. ASPRS class 7, low-point noise, is dropped. Fewer than two kept points is `missing`. Otherwise length is `max(x) - min(x)` and width is `max(y) - min(y)`, and those two numbers go through the same gate as a typed row. A return number above 1 sets clutter. No return column means clutter is false. The worked cloud drops the class-7 point at y = 100, so the span stays 12 m by 40 m:

```
ok points=4 dropped=1 width=12 length=40 echo=return clutter=false
```

## Cloth

`python -m tubewalk cloth examples/ground.csv` is the cloth simulation filter of Zhang and others (2016). The cloud is inverted, so the low ground becomes the high surface. A grid falls with the Verlet step below. A particle that passes the cell height sticks. A free neighbor is pulled to that height. A point within 0.5 of the cloth is ground. The slope pass then keeps a point the cloth missed when it is within one cell of a ground point and within 1 m of that height. The spike at `(1, 1, 10)` is more than 0.5 m above the median of the points within one cell, so it is class 18, high noise. A point more than 0.5 m below that median is class 7. The 0.5 m is this file's cloth threshold. `cut=file` on the line means that. It is not a height written in the ASPRS table. A point 0.5 m to 2 m above the local median is class 4. A point 2 m to 5 m above it is class 5. Above 5 m stays class 18, which is why the spike is not vegetation. Class 3 is the band under 0.5 m when the cloth did not call the point ground. Classes 6, 9, 10, 11, 13, 14, 15, 16, 17, 19, 20, 21, and 22 are named and not assigned. Vegetation, buildings, water, and rail are not labeled from a height alone. Class 8 and class 12 are reserved. A key-point is flag bit 1, value 2, not class 8:

```
ground=8 other=1 class2=8 class1=0 class7=0 class18=1 resolution=1 threshold=0.5 cut=file
```

## Centerline

`python -m tubewalk section examples/tube.csv` does not use the bounding box. Points within 15 m in plan are one station, so a 12 m ring stays together and the next ring does not. The circle is fit in that station. The length is the polyline through the station centers, starting at the smallest x, so a bend is longer than its chord. The width is the median diameter. `rms` is the largest radial root-mean-square. An RMS above 5% of the diameter is not used. The worked tube is straight, so the polyline is 40 m and the circle fits with no residual:

```
ok sections=2 segments=2 points=8 dropped=0 width=12 length=40 closure=0 offset=0 rms=0 echo=return clutter=false
```

## Verlet

The cloth does not store a velocity. It stores where the particle is and where it was.

1. Keep the current height as `old`.
2. The new height is `pos + (pos - old) * (1 - 0.01) - 0.2 * 0.65²`. The last term is gravity times the squared time step, aimed down.
3. If that height is below the inverted point in the cell, set the height to the point and stop the particle.
4. A free neighbor is then moved to the stuck neighbor's height. That is the constraint, not another time step.

## LAZ

LAZ is LAS after LASzip. The compressor does not store the points raw. It predicts the next point from the ones before it, then range-codes the difference. Points are grouped into chunks so a reader can start at a chunk instead of the first point. XYZ, the return byte, and the class use one coder. GPS time and color use others. `python -m tubewalk laz file.laz` calls that decoder through lazrs and then drops class 7 and fits the same circle. This file contains that range coder for its own deltas. It does not decode a `.laz` file. `laz` still calls lazrs. A file that is not LAZ raises `not a laz`.

## LAS

`python -m tubewalk las file.las` reads ASPRS LAS 1.2 formats 0 and 1, and LAS 1.4 formats 6 and 7. The file starts with `LASF`. Version bytes are at 24 and 25. Scales are three doubles at byte 131. Offsets are three doubles at byte 155. A coordinate is `integer * scale + offset`. In 1.2 the return number is the low 3 bits of byte 14 and the class is the low 5 bits of byte 15. In 1.4 format 6 the return number is the low 4 bits of the uint16 at byte 14, the class is the byte at offset 16, and the point count is the uint64 at byte 247. Class 7 is dropped, then the same circle is fit. Anything else raises `not a las`, `not las 1.2 or 1.4`, or `not this las`.

## Range coder

`encode_bits` is the per-bit model. The context is `min(7, bit length)` of the previous residual. Each bit has its own count of zeros and of ones, starting at 1. A value is a zero flag, five length bits, a sign bit, then the magnitude bits under the leading 1. `decode_bits(encode_bits(values))` returns the same integers.

LAS 1.4 formats 6 to 10 name classes 0 through 22. `asprs_name(2)` is `ground`. `asprs_name(8)` and `asprs_name(12)` are `reserved`. `asprs_name(18)` is `high noise`. Codes 23 through 63 are `reserved`. Codes 64 through 255 are `user`. The point-14 class coder uses 256 symbols and 64 instances. The instance is `(previous class mod 32) * 2`, plus 1 when this return number is 1 and the pulse has fewer than 2 returns. Three checks: previous 2 with one return is instance 5, previous 2 with return 2 of 3 is instance 4, previous 40 with one return is instance 17. The first class in a chunk is stored raw. Every symbol starts at count 1, so 256 symbols start at total 256. The point-14 text names the instance, not a different seed table. `encode_laz_index` is the published layout. The first 8 bytes are a little-endian int64, the position of the chunk table in that block. The table starts with version 0 and the chunk count, both unsigned 32-bit. Each chunk then stores two signed deltas: the point count minus the previous count, then the payload length minus the previous length. The previous value starts at 0, so the first delta is the count itself and the first size itself. On the two-chunk check the first count delta is 2. LAZ then compresses those integers with a 32-bit integer compressor and two instances. This file stores the deltas raw. `table` is not that compressor. `CHK1` is the older private index. Neither one decodes a `.laz` file.

## Worked rows

`examples/conduit.csv` uses those four columns and nothing else. Worked rows are not a surveyed tunnel.

## What it will not do

- Treat ok as a keep.
- Treat GRAIL as this catalog.
- Treat a radar line as a ceiling.
- Read LAS 1.4, or a point format other than 0 or 1.
- Decode a `.laz` file with this range coder. `laz` calls lazrs. The coder here round-trips signed deltas only.
- Fit a centerline to a cloud whose stations have fewer than three points.

## Run

```
PYTHONPATH=src python -m unittest tests.test_kernel
PYTHONPATH=src python -m tubewalk examples/conduit.csv
PYTHONPATH=src python -m tubewalk lidar examples/cloud.csv
PYTHONPATH=src python -m tubewalk cloth examples/ground.csv
PYTHONPATH=src python -m tubewalk section examples/tube.csv
```

Copyright 2026 Digital Currensy Inc. Apache-2.0.
