"""Reproduce transparent, assumption-limited tests of the published spectrum.

The archive supplies one-dimensional depths, marginal uncertainties, and four
forward models. No wavelength covariance matrix is supplied, so every test
below is conditional on independent Gaussian bin errors. The literature's
model metadata are preserved rather than silently re-derived.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from scipy.optimize import minimize_scalar
from scipy.stats import chi2

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "spectra" / "SpectraFigureData83602.nc"
FIGURES = ROOT / "figures"
STATS_FILE = FIGURES / "spectrum_statistics.csv"
DIAGNOSTICS_FILE = FIGURES / "spectrum_diagnostics.csv"
FIGURE_FILE = FIGURES / "toi836b_published_spectrum.png"
DIAGNOSTIC_FIGURE = FIGURES / "toi836b_spectrum_residuals.png"
MODEL_NAMES = ("1xSolar", "10xSolar", "250xSolar", "1000xSolar")


def _clean(values, errors):
    values, errors = np.asarray(values, float), np.asarray(errors, float)
    good = np.isfinite(values) & np.isfinite(errors) & (errors > 0)
    return values[good], errors[good]


def flat_test(values, errors):
    values, errors = _clean(values, errors)
    weights = 1 / errors**2
    mean = float(np.sum(weights * values) / np.sum(weights))
    residual = values - mean
    statistic = float(np.sum((residual / errors) ** 2))
    dof = len(values) - 1
    return {"n": len(values), "mean": mean, "chi2": statistic, "dof": dof,
            "reduced_chi2": statistic / dof, "p": float(chi2.sf(statistic, dof)),
            "max_abs_standardized_residual": float(np.max(np.abs(residual / errors)))}


def offset_model_test(values, errors, model_values):
    values, errors = _clean(values, errors)
    model = np.asarray(model_values, float)
    if model.shape != values.shape or not np.all(np.isfinite(model)):
        raise ValueError("Model and valid spectrum bins must have identical finite shapes")
    weights = 1 / errors**2
    offset = float(np.sum(weights * (values - model)) / np.sum(weights))
    fitted = model + offset
    statistic = float(np.sum(((values - fitted) / errors) ** 2))
    dof = len(values) - 1
    return {"n": len(values), "offset": offset, "chi2": statistic, "dof": dof,
            "reduced_chi2": statistic / dof, "p": float(chi2.sf(statistic, dof)),
            "model": fitted}


def leave_one_out_flat(values, errors):
    """Measure how much the flat-spectrum p-value depends on any one bin."""
    values, errors = _clean(values, errors)
    tests = [flat_test(np.delete(values, i), np.delete(errors, i)) for i in range(len(values))]
    probabilities = np.asarray([test["p"] for test in tests])
    return {"p_min": float(probabilities.min()), "p_max": float(probabilities.max()),
            "p_median": float(np.median(probabilities))}


def intrinsic_scatter_mle(values, errors):
    """Fit a non-negative extra-scatter term under an independent normal model."""
    values, errors = _clean(values, errors)

    def objective(jitter):
        variance = errors**2 + jitter**2
        weights = 1 / variance
        mean = np.sum(weights * values) / np.sum(weights)
        return float(np.sum(np.log(variance) + (values - mean) ** 2 / variance))

    upper = max(float(np.std(values)), float(np.median(errors)) * 5)
    fit = minimize_scalar(objective, bounds=(0, upper), method="bounded")
    return float(fit.x)


def write_rows(path, rows):
    fields = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    FIGURES.mkdir(exist_ok=True)
    with xr.open_dataset(DATA_FILE) as dataset:
        wavelength = np.asarray(dataset.wavelength.values, float)
        depth = np.asarray(dataset["ExoTiC-JEDI-transit-depth"].values, float)
        error = np.asarray(dataset["ExoTiC-JEDI-transit-depth-error"].values, float)
        models = {name: np.asarray(dataset[name].values, float) for name in MODEL_NAMES}
        source_sigma = json.loads(dataset.attrs["sigma"])
        source_reduced_chi2 = json.loads(dataset.attrs["chi_square"])

    flat = flat_test(depth, error)
    loo = leave_one_out_flat(depth, error)
    jitter = intrinsic_scatter_mle(depth, error)
    rows = [{"comparison": "weighted flat", **flat}]
    fitted = {}
    for label, model in models.items():
        result = offset_model_test(depth, error, model)
        rows.append({"comparison": label + " + fitted vertical offset",
                     **{key: value for key, value in result.items() if key != "model"},
                     "delta_chi2_vs_flat": result["chi2"] - flat["chi2"],
                     "source_reported_sigma": source_sigma[label],
                     "source_reported_reduced_chi2": source_reduced_chi2[label]})
        fitted[label] = result["model"]
    write_rows(STATS_FILE, rows)
    write_rows(DIAGNOSTICS_FILE, [{"assumption": "independent Gaussian wavelength-bin errors",
                                   "flat_p": flat["p"], "flat_reduced_chi2": flat["reduced_chi2"],
                                   "loo_p_min": loo["p_min"], "loo_p_median": loo["p_median"],
                                   "loo_p_max": loo["p_max"], "intrinsic_scatter_mle_ppm": jitter,
                                   "max_abs_standardized_residual": flat["max_abs_standardized_residual"]}])

    fig, ax = plt.subplots(figsize=(9.4, 5.6))
    ax.errorbar(wavelength, depth, yerr=error, fmt="o", ms=3, color="#17212b",
                ecolor="#78909c", label="ExoTiC-JEDI spectrum")
    ax.axhline(flat["mean"], color="#b54708", lw=2, label="weighted flat")
    for label, model in fitted.items():
        ax.plot(wavelength, model, lw=1.35, alpha=.8, label=label + " model")
    ax.set(xlabel="Wavelength [µm]", ylabel="Transit depth [ppm]",
           title="TOI-836 b — published JWST/NIRSpec G395H spectrum")
    ax.grid(alpha=.2); ax.legend(frameon=False, fontsize=7.5, ncol=2); fig.tight_layout()
    fig.savefig(FIGURE_FILE, dpi=200); plt.close(fig)

    standardized = (depth - flat["mean"]) / error
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.2, 4.3), gridspec_kw={"width_ratios": [2.2, 1]})
    ax1.axhspan(-2, 2, color="#0f766e", alpha=.09, label="±2σ band")
    ax1.axhline(0, color="#52606d", lw=1)
    ax1.errorbar(wavelength, standardized, yerr=np.ones_like(error), fmt="o", ms=3,
                 color="#17212b", ecolor="#a6b2bd")
    ax1.set(xlabel="Wavelength [µm]", ylabel="Standardized residual", title="Flat-model residuals")
    ax1.grid(alpha=.18); ax1.legend(frameon=False, fontsize=8)
    ax2.hist(standardized, bins=12, color="#0f766e", alpha=.82, edgecolor="white")
    ax2.set(xlabel="Standardized residual", ylabel="Bin count", title="Residual distribution")
    ax2.grid(axis="y", alpha=.18)
    fig.suptitle("Diagnostics assume independent Gaussian spectral-bin errors", fontsize=10)
    fig.tight_layout(); fig.savefig(DIAGNOSTIC_FIGURE, dpi=200); plt.close(fig)
    return {"flat": flat, "leave_one_out": loo, "intrinsic_scatter_ppm": jitter,
            "rows": rows, "n": len(depth)}


if __name__ == "__main__":
    result = main()
    loo = result["leave_one_out"]
    print(f"TOI-836 b: {result['n']} bins; flat p={result['flat']['p']:.4f}; "
          f"leave-one-out p={loo['p_min']:.4f}-{loo['p_max']:.4f}; "
          f"extra scatter={result['intrinsic_scatter_ppm']:.1f} ppm")
