# Methods

## Scope and estimands

This repository performs two deliberately separate analyses:

1. a diagnostic fit to public TESS PDCSAP photometry, estimating a local
   timing correction and transit geometry under fixed orbital assumptions;
2. goodness-of-fit diagnostics for the published JWST/NIRSpec G395H
   transmission spectrum and its archived forward models.

It does not perform a joint system fit, atmospheric retrieval, blind transit
search, or independent instrument reduction.

## TESS analysis

Only finite `QUALITY == 0` cadences are retained. PDCSAP flux and uncertainty
are divided by the median flux, followed by one symmetric eight-MAD outlier
rule with a five-percent floor. The analysis uses a window extending three
published durations around the nearest archive-predicted epoch.

A local intercept-and-slope null is compared to a circular `batman` transit
with fixed period, scaled semi-major axis, and quadratic limb darkening. The
fit varies midpoint, radius ratio, impact parameter, intercept, and slope.
The declared support rule is `ΔBIC >= 10`; it is a within-window model
comparison, not a blind-search false-alarm probability.

Sector 11 and Sector 38 are fitted independently. The reported multi-sector
uncertainty multiplies the Jacobian-based depth uncertainty by the square root
of reduced chi-square and by the maximum time-averaging beta over declared
cadence-bin sizes. This is a conservative diagnostic inflation, not a
Gaussian-process covariance model.

## JWST spectrum analysis

The NetCDF artifact supplies 106 ExoTiC-JEDI depth bins, marginal
uncertainties, and four CHIMERA/PICASO forward-model arrays. The flat model and
each atmosphere grid model fit one vertical offset by inverse-variance
weighting. Chi-square reference distributions therefore use 105 degrees of
freedom.

The repository also reports:

- leave-one-bin-out flat-model p-value sensitivity;
- maximum absolute standardized residual;
- non-negative additional scatter fitted by independent-normal likelihood;
- the source-provided model rejection sigma and reduced chi-square metadata.

All spectral tests assume independent Gaussian wavelength-bin errors because
the archived artifact contains no inter-bin covariance matrix. Therefore the
repository's p-values are diagnostics, not a substitute for the source
paper's reduction and retrieval.
