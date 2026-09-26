# Validation record

## Analytic and regression checks

- the archived spectrum contains exactly 106 bins and five declared
  comparisons (flat plus four atmosphere-grid models);
- all fitted statistics are finite and use positive uncertainties;
- the weighted-flat result reproduces `chi2 = 128.4280` for 105 degrees of
  freedom and `p = 0.05994`;
- the source NetCDF rejection metadata reproduce `7.5, 8.2, 3.0, 1.7 sigma`;
- mismatched model arrays fail closed rather than broadcast silently;
- TESS regression tests freeze the depth, midpoint, transit chi-square, and
  delta-BIC results from the committed FITS data;
- every committed TESS sector is either analysed or records an explicit skip;
- generated CSV and figure artifacts must be present and non-empty;
- light/dark core text combinations are checked against WCAG AA contrast.

## Sensitivity result

The weighted-flat spectrum gives `p = 0.05994` under independent Gaussian-bin
errors. Across 106 leave-one-bin-out reruns the p-value spans `0.05238` to
`0.12277`, with median `0.05602`. Thus the conventional five-percent decision
does not depend on one exceptional wavelength bin, but it is close enough to
the threshold that “flat” must be phrased as “not rejected by this test,” not
as proof of a featureless atmosphere.

The fitted additional independent scatter is 7.98 ppm, and the largest flat
model standardized residual is 2.72. These are descriptive diagnostics; no
wavelength covariance was available.
