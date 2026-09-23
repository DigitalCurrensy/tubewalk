"""Two published radar tubes. Declared conduit stats. Not a scored walk."""

MTP = {
    "id": "TUBE-MTP-WEST",
    "name": "Mare Tranquillitatis west conduit",
    "lat": 8.3355,
    "lon": 33.222,
    "alt": (8.336, 33.222),
    "width_m": 45.0,
    "width_unc_m": 7.5,
    "length_m": 30.0,
    "length_hi_m": 80.0,
    "depth_lo_m": 135.0,
    "depth_hi_m": 175.0,
    "echo": "conduit",
    "clutter": False,
    "instrument": "minirf",
    "parent": "BAG-MTP-TRANQ",
    "fetched": False,
}

MHP = {
    "id": "TUBE-MHP-RILLE",
    "name": "Marius Hills rille tube",
    "lat": 14.1,
    "lon": 303.262,
    "alt": (14.091, 303.23),
    "width_m": None,
    "width_unc_m": None,
    "length_m": 50_000.0,
    "length_hi_m": 60_000.0,
    "depth_lo_m": 100.0,
    "depth_hi_m": 225.0,
    "echo": "second",
    "clutter": False,
    "instrument": "lrs",
    "parent": "BAG-MHP-MARIUS",
    "fetched": False,
}

GRAIL = {
    "id": "grail-rille",
    "name": "GRAIL rille A deficit",
    "this_catalog": False,
    "is_radar": False,
    "degree": 1200,
    "cannot_resolve_m": 45,
    "fetched": False,
}

CAPELLA = {
    "id": "capella",
    "name": "Capella terrestrial analog",
    "this_catalog": False,
}
