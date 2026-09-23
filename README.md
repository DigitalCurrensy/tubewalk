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
2. **missing** — `width_m` is missing or `length_m` is missing. A blank is not a measurement. It is not ok.
3. **pinch** — `width_m < 10`.
4. **stub** — `length_m < 30`.
5. **clutter** — `clutter` is true.
6. **ok** — none of the above.

A missing width is still not a pinch. It is missing. A missing length is still not a stub. It is missing.

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
