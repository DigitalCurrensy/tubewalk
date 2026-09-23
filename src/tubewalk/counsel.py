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

"""TUBE COUNSEL PASS. Unsigned. CohRaS named, not run. InSAR is not a walk."""

from __future__ import annotations

from .letter import SAR_SIM, compile_letter

TITLE = "TUBE COUNSEL PASS"
OFFER = "Unsigned. Not an invoice."
COUNSEL = "unsigned"
WORD_CAP = 80

COHRAY = {
    "name": "CohRaS",
    "processing": "coherent ray tracing",
    "engine": "from scratch",
    "phase_law": "two-way φ = 4π R / λ",
    "insar": True,
    "lunar": False,
    "this_letter": False,
    "run": False,
    "vendored": False,
    "is_tube_py": False,
    "scatterers_lo": 1,
    "scatterers_hi": 6,
}

INSAR = {
    "wavelength_cm": 12.6,
    "fringe_s_cm": 6.3,
    "fringe_c_cm": 2.8,
    "transmitter_failed": "2010-12-26",
    "minirf_is_stack": False,
    "stokes_is_stack": False,
    "this_walk": False,
    "fetched": False,
    "scored": False,
}


def _words(body: str) -> int:
    return len([w for w in body.split() if w])


def geometric_optics_valid(wavelength_m: float, scale_m: float) -> bool:
    if wavelength_m != wavelength_m or scale_m != scale_m:
        return False
    if not (wavelength_m > 0 and scale_m > 0):
        return False
    return wavelength_m < scale_m


def fringe_los_m(wavelength_m: float) -> float | None:
    if wavelength_m != wavelength_m or not (wavelength_m > 0):
        return None
    return wavelength_m / 2.0


def compile_counsel(kind: str) -> dict:
    walk = compile_letter("walk")
    base = {
        "title": TITLE,
        "counsel": COUNSEL,
        "engineer_of_record": COUNSEL,
        "signed": False,
        "wet_ink": False,
        "not_a_certificate": True,
        "not_survey_grade": True,
        "walk_stamp": walk["stamp"],
        "walk_issued": walk["issued"],
        "do_not_enter": walk["do_not_enter"],
        "cohras_run": False,
        "insar_is_walk": False,
        "radar_fetched": False,
    }
    if kind == "cohras":
        body = (
            "No counsel pass. CohRaS is coherent ray tracing. Phase is not tube.py. "
            "Speckle via random scatterers is not a walk. Named, not run. "
            "Not this Moon letter. Not a certificate."
        )
        return {
            **base,
            "issued": False,
            "stamp": "refused",
            "why": "cohras_named_not_scored",
            "body": body,
            "words": _words(body),
        }
    if kind == "insar":
        body = (
            "No counsel pass. InSAR maps line-of-sight displacement. A fringe is not a conduit. "
            "PS-InSAR is Earth millimetres. Mini-RF is not a deformation stack. "
            "Not this walk. Not a certificate."
        )
        return {
            **base,
            "issued": False,
            "stamp": "refused",
            "why": "insar_is_not_a_walk",
            "body": body,
            "words": _words(body),
        }
    if kind == "pretty-walk":
        body = (
            "No counsel pass. A pretty cave is not a walk. Google Moon is not a score. "
            "ok still sits. Famous is not a door. Do-not-enter is abort. "
            "Not a certificate. Not survey-grade."
        )
        return {
            **base,
            "issued": False,
            "stamp": "refused",
            "why": "pretty_is_not_a_walk",
            "body": body,
            "words": _words(body),
        }
    if kind == "unnamed-sign":
        body = (
            "No counsel pass. Counsel unnamed. Engineer of record unnamed. "
            "A checked box is not a wet signature. This console does not mint ink. "
            "Not a certificate. Research tool."
        )
        return {
            **base,
            "issued": False,
            "stamp": "refused",
            "why": "unnamed_signature",
            "body": body,
            "words": _words(body),
        }
    if kind == "named-unsigned":
        body = (
            "TUBE COUNSEL PASS. Named seats are not a wet signature. Research tool. "
            "Not a certificate. ok is not a walk. CohRaS unrun. InSAR is not a conduit. "
            "Counsel unsigned. Engineer of record unsigned."
        )
        return {
            **base,
            "issued": True,
            "stamp": "unsigned",
            "why": "names_are_not_wet_ink",
            "body": body,
            "words": _words(body),
        }
    body = (
        "TUBE COUNSEL PASS. Research tool. Not a certificate. Not survey-grade. "
        "TUBE-MTP-WEST still OK. ok is not a walk. Counsel unsigned. "
        "Engineer of record unsigned."
    )
    return {
        **base,
        "issued": True,
        "stamp": "unsigned",
        "why": "compiled_unsigned",
        "body": body,
        "words": _words(body),
    }


def cohras_from_letter() -> dict:
    return next(s for s in SAR_SIM if s["id"] == "cohras")
