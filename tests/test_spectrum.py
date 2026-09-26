"""Reproduction checks for the archived published spectrum."""
from pathlib import Path

import analyze_spectrum as spectrum
import numpy as np


def test_spectrum_analysis_is_finite_and_reproducible():
    result = spectrum.main()
    assert result["n"] == 106
    assert len(result["rows"]) == 5
    assert all(np.isfinite(row["chi2"]) and row["dof"] > 0 for row in result["rows"])
    assert 0.05 < result["flat"]["p"] < 0.07
    assert result["leave_one_out"]["p_min"] > 0.05
    assert result["leave_one_out"]["p_max"] > result["leave_one_out"]["p_min"]
    assert 0 <= result["intrinsic_scatter_ppm"] < 15
    assert [row["source_reported_sigma"] for row in result["rows"][1:]] == [7.5, 8.2, 3.0, 1.7]
    for path in (spectrum.STATS_FILE, spectrum.DIAGNOSTICS_FILE,
                 spectrum.FIGURE_FILE, spectrum.DIAGNOSTIC_FIGURE):
        assert Path(path).is_file() and Path(path).stat().st_size > 100


def test_invalid_model_shape_fails_closed():
    with np.testing.assert_raises(ValueError):
        spectrum.offset_model_test([1, 2], [0.1, 0.1], [1])
