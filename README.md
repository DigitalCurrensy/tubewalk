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

This is not a ground filter, a centerline, a fitted cylinder, or a LAS reader. Classification, a cloth filter, and a mesh are different programs.

## Worked rows

`examples/conduit.csv` uses those four columns and nothing else. Worked rows are not a surveyed tunnel.

## What it will not do

- Treat ok as a keep.
- Treat GRAIL as this catalog.
- Treat a radar line as a ceiling.
- Read a LAS or LAZ file.
- Fit a centerline or a cylinder to the points.

## Run

```
PYTHONPATH=src python -m unittest tests.test_kernel
PYTHONPATH=src python -m tubewalk examples/conduit.csv
PYTHONPATH=src python -m tubewalk lidar examples/cloud.csv
```

Copyright 2026 Digital Currensy Inc. Apache-2.0.
