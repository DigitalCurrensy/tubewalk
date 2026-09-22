# TUBEWALK

The tube is the walk beyond the mouth. A radar echo looks like a cave you can walk. Name the conduit.

**Owner:** Digital Currensy Inc.
**Status:** Private. Independent tool. Not a NASA Space Apps 2026 submission.
**License of our code:** Apache-2.0

## One sentence

A radar echo looks like a cave you can walk. Name the conduit against echo, width, and length — or say the tube is not a walk.

## Wave freeze

- W0 catalog: Mare Tranquillitatis west Mini-RF conduit (Carrer 2024) and Marius Hills LRS rille (Kaku 2017). tube.py named, not run.
- W1 tube scorer: tube.py ported. Dark first. Catalog scores ok. Mini-RF Stokes named, not scored. LRS tanδ named, not scored.
- W2 one bad tube: TUBE-MTP-WEST walked. Catalog ok is not a walk. RaySAR inversion named, not run. GRAIL gravity named, not radar.
- W3 tube letter: TUBE LETTER compiled. Fail still issues. ok still issues. ok is not a walk. 3D SAR named. A mascon is not a conduit. Counsel unsigned.
- W4 counsel pass: unsigned. CohRaS named, not run. InSAR deformation is not a conduit. A fringe is not a walk. TUBEWALK W0–W4 frozen.

## tube.py

```
if echo is None or echo == none: dark
elif width_m is not None and width_m < 10: pinch
elif length_m is not None and length_m < 30: stub
elif clutter: clutter
else: ok
```

Dark first. Equality sits. Radar unfetched. ok is not a walk.

## What it is not

- Not BAGHOLD mouth score. A bag is a goal you enter. A tube is the walk beyond.
- Not Mini-RF mixed with LRS. Dual instruments named.
- Not GRAIL gravity as radar. A 45 m conduit is below GRGM1200A's floor.
- Not RaySAR run. Inversion named. POV-Ray stays upstream.
- Not SARViz as a ceiling invert. Rasterization cannot do bounce 3.
- Not CohRaS run. Coherent ray tracing named. Phase is not tube.py.
- Not InSAR deformation as a walk. A fringe is not a conduit.
- Not a mascon as a conduit. Positive gravity is not an empty tube.
- Not DEM void fraction as a radar void.
- Not FEASFRONT lighting. A dark conduit is not a walk.

## Run

```
PYTHONPATH=src python -m unittest tests.test_kernel
```
