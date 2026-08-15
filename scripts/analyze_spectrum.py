from __future__ import annotations
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import chi2

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "spectra"
FIGURES = ROOT / "figures"
STATS_FILE = FIGURES / "spectrum_statistics.csv"

def flat_test(values, errors):
    values, errors = np.asarray(values, float), np.asarray(errors, float)
    good = np.isfinite(values) & np.isfinite(errors) & (errors > 0)
    values, errors = values[good], errors[good]
    weights = 1 / errors**2
    mean = np.sum(weights * values) / np.sum(weights)
    statistic = np.sum(((values - mean) / errors)**2)
    dof = len(values) - 1
    return {"n": len(values), "mean": mean, "chi2": statistic, "dof": dof,
            "p": chi2.sf(statistic, dof)}

def offset_model_test(wavelength, values, errors, model_wavelength, model_values):
    model = np.interp(wavelength, model_wavelength, model_values)
    weights = 1 / errors**2
    offset = np.sum(weights * (values - model)) / np.sum(weights)
    statistic = np.sum(((values - model - offset) / errors)**2)
    dof = len(values) - 1
    return {"n": len(values), "offset": offset, "chi2": statistic,
            "dof": dof, "p": chi2.sf(statistic, dof), "model": model + offset}

def write_rows(rows):
    fields = sorted({key for row in rows for key in row})
    with STATS_FILE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)

import xarray as xr

FIGURE_FILE = FIGURES / "toi836b_published_spectrum.png"

def main():
    FIGURES.mkdir(exist_ok=True)
    with xr.open_dataset(DATA / "SpectraFigureData83602.nc") as dataset:
        wavelength = dataset.wavelength.values
        depth = dataset["ExoTiC-JEDI-transit-depth"].values
        error = dataset["ExoTiC-JEDI-transit-depth-error"].values
        models = {name: dataset[name].values for name in ("1xSolar", "10xSolar", "250xSolar", "1000xSolar")}
    flat = flat_test(depth, error); rows = [{"comparison": "weighted flat", **flat}]
    fitted = {}
    for label, model in models.items():
        result = offset_model_test(wavelength, depth, error, wavelength, model)
        rows.append({"comparison": label + " + fitted vertical offset",
                     **{key: value for key, value in result.items() if key != "model"}})
        fitted[label] = result["model"]
    write_rows(rows)
    fig, ax = plt.subplots(figsize=(9.2, 5.3))
    ax.errorbar(wavelength, depth, yerr=error, fmt="o", ms=3, color="#17212b", ecolor="#78909c", label="ExoTiC-JEDI spectrum")
    for label, model in fitted.items(): ax.plot(wavelength, model, lw=1.6, label=label + " model (offset fitted)")
    ax.set(xlabel="Wavelength [micron]", ylabel="Transit depth [ppm]",
           title="TOI-836 b: published JWST NIRSpec/G395H transmission spectrum")
    ax.grid(alpha=.2); ax.legend(frameon=False, fontsize=8, ncol=2); fig.tight_layout()
    fig.savefig(FIGURE_FILE, dpi=190); plt.close(fig)
    return {"flat": flat, "rows": rows, "n": len(depth)}

if __name__ == "__main__":
    result = main(); print(f"TOI-836 b: {result['n']} spectral bins; flat-spectrum p={result['flat']['p']:.3g}")
