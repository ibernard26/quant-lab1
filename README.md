# quant-lab1

A small, educational quantitative-finance laboratory built from first
principles while learning quantitative finance and Python together. The
calculations are written out by hand (no NumPy/Pandas) so every mathematical
step stays visible and reviewable.

## Pipeline

```
prices
  -> returns
  -> mean return
  -> deviations
  -> squared deviations
  -> population variance      (divide by n)
  -> population std / volatility
  -> annualized volatility    (daily volatility * sqrt(252))
  -> sample variance          (divide by n - 1)
  -> sample standard deviation
  -> excess returns           (returns minus the per-period risk-free rate)
  -> Sharpe ratio             (mean excess / std of excess)
  -> annualized Sharpe ratio  (daily Sharpe * sqrt(252))
```

Run the program:

```
python3 main.py
```

Run the tests:

```
python3 -m unittest -v
```

## Population variance vs. sample variance

Both measure spread around the mean, but they divide the summed squared
deviations by a different amount:

```
Population variance:   sigma^2 = sum((x_i - x_bar)^2) / n
Sample variance:       s^2     = sum((x_i - x_bar)^2) / (n - 1)
```

Dividing by `n - 1` (Bessel's correction) makes the sample variance an
unbiased estimate of the variance of the underlying population when you only
have a finite sample. Because it divides by `n - 1`, sample variance needs at
least two observations.

Financial return observations are usually treated as a **sample** drawn from an
unknown return-generating process (we can never observe every possible return),
so sample statistics are the natural choice for estimating risk. This project
keeps **both**: `calculate_variance` (population) is preserved from the earlier
milestone for educational comparison, and `calculate_sample_variance` /
`calculate_sample_standard_deviation` add the sample versions alongside it. The
two are kept as separate functions so the `n` vs. `n - 1` distinction stays
obvious in the code.

## Sharpe-ratio assumptions

The Sharpe ratio implementation is intentionally explicit about frequency and
units:

- **Returns** are **daily decimal** returns (5% is `0.05`, not `5`).
- **Risk-free rate** is supplied as an **annual decimal** rate and converted to
  a daily rate by compounding, so the numerator and denominator share the same
  daily frequency:

  ```
  daily_rate = (1 + annual_rate) ** (1 / 252) - 1
  ```

  (This compounding conversion is used instead of the rough `annual / 252`
  approximation.)

- **Excess return** for each day is `return - daily_risk_free_rate`.
- The **Sharpe ratio** is `mean(excess returns) / standard_deviation(excess
  returns)`, using the **sample** standard deviation (divide by `n - 1`).
- The **annualized Sharpe ratio** scales the daily Sharpe by `sqrt(252)`.

Negative Sharpe ratios are valid (they mean the average return did not beat the
risk-free rate). If the excess returns have zero spread, the Sharpe ratio is
undefined and the code raises a clear error instead of dividing by zero.

`252` is the conventional number of trading days per year.
