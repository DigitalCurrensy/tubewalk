# TUBEWALK

The caller supplies width, length, echo, and clutter.

**Owner:** Digital Currensy Inc.
**Copyright:** 2026 Digital Currensy Inc.
**License:** Apache-2.0. The file named LICENSE is the unmodified Apache text. The copyright notice is in NOTICE and at the top of each source file.

## What it decides

A name for that conduit, or a refusal. ok is not a keep. GRAIL is not this catalog.

## The order inside walk()

`walk(width_m, length_m, echo, clutter)` returns the first hit, in this order:

1. **dark** — `echo` is missing, or `echo` is the string `none`.
2. **pinch** — `width_m` is present and `width_m < 10`.
3. **stub** — `length_m` is present and `length_m < 30`.
4. **clutter** — `clutter` is true.
5. **ok** — none of the above.

A blank numeric cell is missing. It is the same branch `walk()` already uses for `None`: a missing width is not a pinch, and a missing length is not a stub. Later checks still run. ok is not a keep. A radar line is not a ceiling.

## Worked rows

`examples/conduit.csv` uses those four columns and nothing else. Worked rows are not a surveyed tunnel.

## What it will not do

- Treat ok as a keep.
- Treat GRAIL as this catalog.
- Treat a radar line as a ceiling.

## Run

```
PYTHONPATH=src python -m unittest tests.test_kernel
PYTHONPATH=src python -m tubewalk examples/conduit.csv
```

Copyright 2026 Digital Currensy Inc. Apache-2.0.
