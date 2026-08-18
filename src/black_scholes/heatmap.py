"""Price-surface calculation and interactive Seaborn visualisations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

from .core import OptionType, OptionTypeLike, black_scholes_price

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure


@dataclass(frozen=True, slots=True)
class HeatmapData:
    """Numerical data underlying a spot/volatility price heatmap."""

    spot_prices: tuple[float, ...]
    volatilities: tuple[float, ...]
    prices: tuple[tuple[float, ...], ...]


def _axis(values: Sequence[float], name: str, *, positive: bool) -> tuple[float, ...]:
    converted = tuple(float(value) for value in values)
    if not converted:
        raise ValueError(f"{name} must contain at least one value")
    if positive and any(value <= 0 for value in converted):
        raise ValueError(f"all {name} values must be greater than zero")
    if not positive and any(value < 0 for value in converted):
        raise ValueError(f"all {name} values must be non-negative")
    return converted


def price_heatmap_data(
    spot_prices: Sequence[float],
    volatilities: Sequence[float],
    *,
    strike: float,
    time_to_expiry: float,
    risk_free_rate: float = 0.0,
    option_type: OptionTypeLike = OptionType.CALL,
    dividend_yield: float = 0.0,
) -> HeatmapData:
    """Calculate a price matrix with volatility rows and spot-price columns."""

    spots = _axis(spot_prices, "spot_prices", positive=True)
    vols = _axis(volatilities, "volatilities", positive=False)
    prices = tuple(
        tuple(
            black_scholes_price(
                spot,
                strike,
                time_to_expiry,
                volatility,
                risk_free_rate,
                option_type,
                dividend_yield,
            )
            for spot in spots
        )
        for volatility in vols
    )
    return HeatmapData(spots, vols, prices)


def plot_price_heatmap(
    spot_prices: Sequence[float],
    volatilities: Sequence[float],
    *,
    strike: float,
    time_to_expiry: float,
    risk_free_rate: float = 0.0,
    option_type: OptionTypeLike = OptionType.CALL,
    dividend_yield: float = 0.0,
    annotate: bool = True,
    cmap: str = "viridis",
    title: str | None = None,
    ax: Axes | None = None,
    show: bool = True,
) -> tuple[Figure, Axes, HeatmapData]:
    """Display and return a Seaborn Black-Scholes price heatmap.

    The figure is kept in memory and is never written to disk. Matplotlib and
    Seaborn are imported only when plotting, keeping the numeric API lightweight.
    """

    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise ImportError(
            "Visualisations require matplotlib and seaborn: "
            "pip install matplotlib seaborn"
        ) from exc

    data = price_heatmap_data(
        spot_prices,
        volatilities,
        strike=strike,
        time_to_expiry=time_to_expiry,
        risk_free_rate=risk_free_rate,
        option_type=option_type,
        dividend_yield=dividend_yield,
    )
    if ax is None:
        sns.set_theme(style="whitegrid", context="notebook")
        figure, ax = plt.subplots(figsize=(11, 6.5))
    else:
        figure = ax.figure

    sns.heatmap(
        data.prices,
        ax=ax,
        annot=annotate,
        fmt=".2f",
        cmap=cmap,
        linewidths=0.5,
        linecolor="white",
        xticklabels=[f"${value:g}" for value in data.spot_prices],
        yticklabels=[f"{value:.1%}" for value in data.volatilities],
        cbar_kws={"label": "Option price"},
    )
    ax.set_xlabel("Underlying spot price", labelpad=10)
    ax.set_ylabel("Volatility", labelpad=10)
    kind = OptionType(option_type.lower()) if isinstance(option_type, str) else OptionType(option_type)
    ax.set_title(title or f"Black-Scholes {kind.value.title()} Price Heatmap (K={strike:g})")

    figure.tight_layout()
    if show:
        plt.show()
    return figure, ax, data


def plot_price_curves(
    spot_prices: Sequence[float],
    volatilities: Sequence[float],
    *,
    strike: float,
    time_to_expiry: float,
    risk_free_rate: float = 0.0,
    option_type: OptionTypeLike = OptionType.CALL,
    dividend_yield: float = 0.0,
    title: str | None = None,
    ax: Axes | None = None,
    show: bool = True,
) -> tuple[Figure, Axes, HeatmapData]:

    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise ImportError(
            "Visualisations require matplotlib and seaborn: "
            "pip install matplotlib seaborn"
        ) from exc

    data = price_heatmap_data(
        spot_prices,
        volatilities,
        strike=strike,
        time_to_expiry=time_to_expiry,
        risk_free_rate=risk_free_rate,
        option_type=option_type,
        dividend_yield=dividend_yield,
    )
    if ax is None:
        sns.set_theme(style="whitegrid", context="notebook")
        figure, ax = plt.subplots(figsize=(11, 6.5))
    else:
        figure = ax.figure

    palette = sns.color_palette("mako", n_colors=len(data.volatilities))
    for volatility, prices, color in zip(data.volatilities, data.prices, palette):
        sns.lineplot(
            x=data.spot_prices,
            y=prices,
            ax=ax,
            marker="o",
            linewidth=2.2,
            color=color,
            label=f"{volatility:.1%} vol",
        )

    kind = OptionType(option_type.lower()) if isinstance(option_type, str) else OptionType(option_type)
    ax.axvline(strike, color="#d95f02", linestyle="--", linewidth=1.5, label="Strike")
    ax.set(
        xlabel="Underlying spot price",
        ylabel="Option price",
        title=title or f"Black-Scholes {kind.value.title()} Price Curves (K={strike:g})",
    )
    ax.legend(title="Scenario", frameon=True)
    figure.tight_layout()
    if show:
        plt.show()
    return figure, ax, data
