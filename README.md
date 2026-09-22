# TUBEWALK

The tube is the walk beyond the mouth. A radar echo looks like a cave you can walk. Name the conduit.

**Owner:** Digital Currensy Inc.
**Status:** Private. Independent tool. Not a NASA Space Apps 2026 submission.
**License of our code:** Apache-2.0

## One sentence

A radar echo looks like a cave you can walk. Name the conduit against echo, width, and length — or say the tube is not a walk.

## Wave freeze

- W0 catalog: Mare Tranquillitatis west Mini-RF conduit (Carrer 2024) and Marius Hills LRS rille (Kaku 2017). tube.py named, not run.

W1 tube scorer waits.

## tube.py

```
if echo is None or echo == none: dark
elif width_m is not None and width_m < 10: pinch
elif length_m is not None and length_m < 30: stub
elif clutter: clutter
else: ok
```

Dark first. Equality sits. Radar unfetched.

## What it is not

- Not BAGHOLD mouth score. A bag is a goal you enter. A tube is the walk beyond.
- Not Mini-RF mixed with LRS. Dual instruments named.
- Not GRAIL gravity as radar.
- Not DEM void fraction as a radar void.
- Not FEASFRONT lighting. A dark conduit is not a walk.

## Run

```
PYTHONPATH=src python -m unittest tests.test_kernel
```
