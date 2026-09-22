def walk(
    width_m: float | None,
    length_m: float | None,
    echo: str | None,
    clutter: bool,
) -> str:
    if echo is None or echo == "none":
        return "dark"
    if width_m is not None and width_m < 10:
        return "pinch"
    if length_m is not None and length_m < 30:
        return "stub"
    if clutter:
        return "clutter"
    return "ok"
