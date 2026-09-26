"""Integrity checks for the exact public artifacts used by the analyses."""

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SHA256 = {
    "data/tess2019112060037-s0011-0000000440887364-0143-s_lc.fits":
        "069dc0c0d0abf6ea9ae73ce2830ab940f933abf196752831fbba783d9dba41a7",
    "data/tess2021118034608-s0038-0000000440887364-0209-s_lc.fits":
        "e3e256890f54c1c1c82511abeb59b28dc9c7fa49a3408a15d447931c605a80ea",
    "data/spectra/SpectraFigureData83602.nc":
        "208a6bb0c4f66f54c74f7f442ad5e563ca4eec552b18e58a75deeb0f3084d1b8",
}


def test_archived_inputs_match_declared_checksums():
    for relative_path, expected in EXPECTED_SHA256.items():
        path = ROOT / relative_path
        assert path.is_file(), f"missing archived input: {relative_path}"
        measured = hashlib.sha256(path.read_bytes()).hexdigest()
        assert measured == expected, f"checksum mismatch: {relative_path}"


def test_source_manifest_names_every_archived_input():
    manifest = (ROOT / "data" / "SOURCE.md").read_text(encoding="utf-8")
    for relative_path, checksum in EXPECTED_SHA256.items():
        assert Path(relative_path).name in manifest
        assert checksum in manifest
