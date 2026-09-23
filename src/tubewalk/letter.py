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

"""TUBE LETTER. Paper on the conduit. Fail still issues. ok is not a walk. Not a certificate."""

from __future__ import annotations

from .tube import walk
from .tubes import MTP
from .walk import MTP_WALK

TITLE = "TUBE LETTER"
OFFER = "Unsigned. Not an invoice."
COUNSEL = "unsigned"
WORD_CAP = 80
BOUNCE_NEED = 3
SARVIZ_MAX = 2

SAR_SIM = (
    {
        "id": "raysar",
        "processing": "ray tracing",
        "engine": "adapted POV-Ray",
        "speckle": False,
        "insar": False,
        "bounce_need": 3,
        "can_invert_ceiling": True,
        "run": False,
        "vendored": False,
        "this_letter": False,
    },
    {
        "id": "cohras",
        "processing": "coherent ray tracing",
        "engine": "from scratch",
        "speckle": True,
        "insar": True,
        "bounce_need": 3,
        "can_invert_ceiling": True,
        "run": False,
        "vendored": False,
        "this_letter": False,
    },
    {
        "id": "sarviz",
        "processing": "rasterization",
        "engine": "GPU DirectX",
        "speckle": True,
        "insar": False,
        "bounce_need": 3,
        "can_invert_ceiling": False,
        "run": False,
        "vendored": False,
        "this_letter": False,
    },
    {
        "id": "sbr",
        "processing": "shooting and bouncing ray",
        "engine": "GO+PO",
        "speckle": False,
        "insar": False,
        "bounce_need": 3,
        "can_invert_ceiling": True,
        "run": False,
        "vendored": False,
        "this_letter": False,
    },
)

MASCONS = (
    {
        "id": "imbrium",
        "lat": 34.72,
        "lon": 345.09,
        "diameter_km": 1145.53,
        "anomaly_mgal": 158,
        "this_letter": False,
    },
    {
        "id": "serenitatis",
        "lat": 27.29,
        "lon": 18.36,
        "diameter_km": 674.28,
        "anomaly_mgal": 198.5,
        "this_letter": False,
    },
    {
        "id": "orientale",
        "lat": -19.87,
        "lon": 265.33,
        "diameter_km": 294.15,
        "anomaly_mgal": 180,
        "annulus_mgal": -174.5,
        "this_letter": False,
    },
)


def _words(body: str) -> int:
    return len([w for w in body.split() if w])


def rasterization_can_invert_ceiling() -> bool:
    viz = next(s for s in SAR_SIM if s["id"] == "sarviz")
    return bool(viz["can_invert_ceiling"])


def compile_letter(kind: str) -> dict:
    if kind == "mascon":
        body = (
            "No letter issued. A mascon is not a conduit. "
            "Imbrium is hundreds of km. Positive gravity is not an empty tube. "
            "Not this letter. Not survey-grade."
        )
        return {
            "title": TITLE,
            "issued": False,
            "stamp": "refused",
            "tube_id": None,
            "why": "not_this_letter",
            "body": body,
            "words": _words(body),
            "counsel": COUNSEL,
            "do_not_enter": False,
            "mascon_is_this_letter": False,
            "not_a_certificate": True,
            "not_survey_grade": True,
        }
    if kind == "mhp":
        body = (
            "No letter issued. Marius Hills rille is a different tube. "
            "One walk remains TUBE-MTP-WEST. GRAIL 60 km is not this letter. "
            "Not survey-grade."
        )
        return {
            "title": TITLE,
            "issued": False,
            "stamp": "refused",
            "tube_id": "TUBE-MHP-RILLE",
            "why": "not_this_letter",
            "body": body,
            "words": _words(body),
            "counsel": COUNSEL,
            "do_not_enter": False,
            "mhp_is_this_letter": False,
            "not_a_certificate": True,
            "not_survey_grade": True,
        }
    if kind == "okform":
        body = (
            "TUBE LETTER. Synthetic walk-in vs SYN-TUBE-FLAT. OK. Not TUBE-MTP-WEST. "
            "Different tube. ok is not survey-grade. Not a certificate. Counsel unsigned."
        )
        return {
            "title": TITLE,
            "issued": True,
            "stamp": "ok",
            "tube_id": "SYN-TUBE-FLAT",
            "why": "ok_form_other_tube",
            "body": body,
            "words": _words(body),
            "counsel": COUNSEL,
            "do_not_enter": False,
            "not_a_certificate": True,
            "not_survey_grade": True,
        }
    if kind == "undeclared":
        body = (
            "No letter issued. TUBE-MTP-WEST identity is off. Undeclared is not a tube. "
            "Not a certificate. Not survey-grade."
        )
        return {
            "title": TITLE,
            "issued": False,
            "stamp": "refused",
            "tube_id": MTP_WALK["id"],
            "why": "undeclared_identity",
            "body": body,
            "words": _words(body),
            "counsel": COUNSEL,
            "do_not_enter": False,
            "not_a_certificate": True,
            "not_survey_grade": True,
        }
    if kind == "sarsim":
        body = (
            "TUBE LETTER. TUBE-MTP-WEST vs SYN-TUBE-MTP. OK. RaySAR, CohRaS, and SARViz named. "
            "Rasterization cannot invert a ceiling. Bounce 3 is not tube.py. "
            "Not survey-grade. Counsel unsigned."
        )
        return {
            "title": TITLE,
            "issued": True,
            "stamp": "ok",
            "tube_id": MTP["id"],
            "why": "sarsim_named_not_scored",
            "body": body,
            "words": _words(body),
            "counsel": COUNSEL,
            "do_not_enter": True,
            "sarsim_run": False,
            "not_a_certificate": True,
            "not_survey_grade": True,
        }
    stamp = walk(MTP["width_m"], MTP["length_m"], MTP["echo"], MTP["clutter"])
    body = (
        "TUBE LETTER. TUBE-MTP-WEST vs SYN-TUBE-MTP. OK. Width 45 sits. Length 30 sits. "
        "ok is not a walk. Famous is not a cave. Not survey-grade. Counsel unsigned."
    )
    return {
        "title": TITLE,
        "issued": True,
        "stamp": stamp,
        "tube_id": MTP["id"],
        "why": stamp,
        "body": body,
        "words": _words(body),
        "counsel": COUNSEL,
        "do_not_enter": True,
        "not_a_certificate": True,
        "not_survey_grade": True,
    }
