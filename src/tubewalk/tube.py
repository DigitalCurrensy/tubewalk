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

def walk(
    width_m: float | None,
    length_m: float | None,
    echo: str | None,
    clutter: bool,
) -> str:
    if echo is None or echo == "none":
        return "dark"
    if width_m is None or length_m is None:
        return "missing"
    if width_m < 0 or length_m < 0:
        return "missing"
    if width_m < 10:
        return "pinch"
    if length_m < 30:
        return "stub"
    if clutter:
        return "clutter"
    return "ok"
