# TUBEWALK

TUBEWALK names a radar conduit. A bright line on a radargram is not a ceiling, and it is not a cave you can walk.

**Owner:** Digital Currensy Inc.
**License:** Apache-2.0. Our code only. Cited radar papers stay with their authors.

## What it decides

A named conduit, or a refusal. An `ok` from the shape check is not a keep.

## The rule

The desk scores the walk beyond the mouth: width, pinch, darkness, a stub, clutter, a null width, and missing inputs. Gravity from another instrument is not this tube. A radar geometry that passes is still not a roof.

## Worked cases

The Mare Tranquillitatis west conduit, the Marius Hills rille, and synthetic conduits in this repository. The published names are the papers’ names. The synthetic cases force one gate each. None of them is a surveyed tunnel.

## What it will not do

- Turn a radar line into a ceiling.
- Fetch the radar product in order to print the score.
- Treat a shape check as a structural keep.

## Run

```
PYTHONPATH=src python -m unittest tests.test_kernel
```

Notes under `docs/` are the build record. This page is the description.
