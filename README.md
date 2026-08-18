# Black-Scholes Option Pricer

A reusable Python package for pricing dividend-paying European calls and puts,
calculating analytical Greeks, and displaying Seaborn option-price graphs and
heatmaps over spot price and implied volatility.

## Design and model assumptions

The implementation uses the standard Black-Scholes-Merton closed form with a
continuous dividend yield. Its assumptions are European exercise, lognormal
underlying returns, constant volatility and rates, frictionless markets, and
no arbitrage. It is not an American-option, discrete-dividend, stochastic-rate,
or volatility-smile model.

For a call, the implemented equation is:

`C = S exp(-qT) N(d1) - K exp(-rT) N(d2)`

and put value follows the corresponding put equation. The heatmap places spot
price on the horizontal axis and volatility on the vertical axis because this
makes moneyness and volatility sensitivity visible at the same time. Values are
annotated for quick reading and the color scale preserves the overall surface.

References used for the design:

- Black, F. and Scholes, M. (1973), *The Pricing of Options and Corporate Liabilities*.
- Merton, R. C. (1973), *Theory of Rational Option Pricing* (continuous dividends).
- John C. Hull, *Options, Futures, and Other Derivatives* (formula and Greek conventions).
- Matplotlib `imshow` documentation (matrix-oriented heatmap rendering).

## Install

From this directory:

```powershell
python -m pip install -e .
```

## Python API

```python
from black_scholes import (
    BlackScholesModel,
    black_scholes_price,
    plot_price_curves,
    plot_price_heatmap,
)

# Minimal functional API
call_price = black_scholes_price(
    spot=100,
    strike=100,
    time_to_expiry=1.0,
    volatility=0.20,
    risk_free_rate=0.05,
    option_type="call",
)

# Reusable object API with price and Greeks
model = BlackScholesModel(
    spot=100,
    strike=100,
    time_to_expiry=1.0,
    volatility=0.20,
    risk_free_rate=0.05,
)
print(model.calculate("call").as_dict())

# Heatmap: volatility rows, spot-price columns
figure, axes, data = plot_price_heatmap(
    spot_prices=[70, 80, 90, 100, 110, 120, 130],
    volatilities=[0.10, 0.20, 0.30, 0.40, 0.50],
    strike=100,
    time_to_expiry=1.0,
    risk_free_rate=0.05,
    option_type="call",
    show=True,
)

# A second interactive graph compares price curves across volatility levels.
plot_price_curves(
    spot_prices=[70, 80, 90, 100, 110, 120, 130],
    volatilities=[0.10, 0.20, 0.30, 0.40, 0.50],
    strike=100,
    time_to_expiry=1.0,
    risk_free_rate=0.05,
)
```

Plots are displayed interactively and kept in memory. The plotting API does
not create directories, PNGs, or other output files.

Inputs use decimal annual units: `0.20` means 20% volatility, `0.05` means a
5% continuously compounded rate, and `30 / 365` means 30 days to expiry. Vega
and rho report sensitivity to a 1.00 absolute change; divide by 100 for a
one-percentage-point move. Theta is annual.

The numeric-only `price_heatmap_data(...)` API does not import Matplotlib and is
appropriate for web services that want to render the returned matrix elsewhere.

## CLI

```powershell
black-scholes --spot 100 --strike 100 --time 1 --volatility 0.2 --rate 0.05 `
  --type call --heatmap --curves
```

The command prints price/Greeks as JSON and optionally displays graphs. It can
also read the pricing values from a basic JSON file without changing that file:

```json
{
  "spot": 100,
  "strike": 100,
  "time": 1,
  "volatility": 0.2,
  "rate": 0.05,
  "dividend": 0.0,
  "type": "call"
}
```

```powershell
black-scholes --config option.json --heatmap
```

## Test

```powershell
python -m unittest discover -s tests -v
```
