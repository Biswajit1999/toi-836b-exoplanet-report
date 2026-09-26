# Limitations and claim boundary

- The JWST file is a published one-dimensional product. This repository does
  not reproduce detector calibration, light-curve fitting, spectral
  extraction, or pipeline-to-pipeline systematics.
- No wavelength covariance matrix is included. Spectral p-values assume
  independent marginal errors and can be miscalibrated if bins covary.
- A non-rejected flat line is not evidence that the atmosphere is absent,
  cloud-free, high-metallicity, or uniquely composed.
- The model-grid exclusions are conditional on the source paper's chemistry,
  thermal structure, reference radius/pressure, cloud assumptions, and the
  stated 0.1-bar opaque-pressure boundary.
- “Below 250 times solar” describes a tested clear-atmosphere model space; it
  is not a continuous, prior-independent metallicity posterior.
- The TESS fits use PDCSAP products, fixed limb darkening, fixed period,
  circular geometry, and a local linear baseline. A global transit/timing fit
  with physical priors remains authoritative.
- Beta inflation is a scalar approximation to correlated noise and does not
  encode a time-domain covariance kernel.
- The AI-generated hero is an illustration, not an observation of TOI-836 b.
