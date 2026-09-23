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

`python -m tubewalk cloth examples/ground.csv` is the cloth simulation filter of Zhang and others (2016), without the slope post-process. The cloud is inverted, so the low ground becomes the high surface. A grid falls with the Verlet step `pos + (pos - old) * (1 - 0.01) - 0.2 * 0.65²`. A particle that passes the cell height sticks. A free neighbor is pulled to that height. A point within 0.5 of the cloth is ground. The spike at `(1, 1, 10)` is not:

```
ground=8 other=1 resolution=1 threshold=0.5
```

## Centerline

`python -m tubewalk section examples/tube.csv` does not use the bounding box. The centerline is the long horizontal axis. Each 1 m station with at least three points gets one algebraic circle in the `(offset, z)` plane. The width is the median diameter. The length is the extent along the centerline. The worked tube runs along Y, so the box treats 12 m as the length and says `stub`. The circle does not:

```
ok sections=2 points=8 dropped=0 width=12 length=40 echo=return clutter=false
```

## LAS 1.2

`python -m tubewalk las file.las` reads ASPRS LAS 1.2, point format 0 or 1. The file starts with `LASF`. Version bytes are at 24 and 25. The header size, point offset, format, record length, and count are at byte 94. Scales are three doubles at byte 131. Offsets are three doubles at byte 155. A coordinate is `integer * scale + offset`. The return number is the low 3 bits of point byte 14. The class is the low 5 bits of point byte 15. Formats 0 and 1 only. LAZ is compressed and is not read. Class 7 is dropped, then the same circle is fit. A file that is not this LAS raises `not a las`, `not las 1.2`, or `not this las`.

## Worked rows

`examples/conduit.csv` uses those four columns and nothing else. Worked rows are not a surveyed tunnel.

## What it will not do

- Treat ok as a keep.
- Treat GRAIL as this catalog.
- Treat a radar line as a ceiling.
- Read a LAS or LAZ file other than LAS 1.2 point format 0 or 1.
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
