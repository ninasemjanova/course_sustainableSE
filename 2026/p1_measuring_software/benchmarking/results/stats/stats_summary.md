# Statistical analysis

- Runs used: **300**
- Toolchains: **15**

## One-way ANOVA by toolchain

- Energy: `F(14, 285) = 282.60`, `p = 6.991e-158`, eta^2 `= 0.933`
- Time: `F(14, 285) = 390.91`, `p = 9.487e-177`, eta^2 `= 0.951`

## Linear regression (Energy vs Time, all runs)

- Model: `energy_J = 268.69 + 19.42 * time_s`
- `R^2 = 0.9645`, `r = 0.9821`, `p = 5.421e-218`
- Slope 95% CI: `[19.00, 19.85]` J/s

## Outputs

- `energy_time_regression.png`
- `anova_tukey_energy.csv`
- `anova_tukey_time.csv`
