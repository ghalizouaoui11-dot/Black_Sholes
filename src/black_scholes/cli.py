
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .core import black_scholes
from .heatmap import plot_price_curves, plot_price_heatmap


def _range(start: float, stop: float, count: int) -> list[float]:
    if count < 2:
        raise ValueError("heatmap point counts must be at least 2")
    step = (stop - start) / (count - 1)
    return [start + index * step for index in range(count)]


def load_json_config(file_path: str | Path) -> dict[str, Any]:
    """Read a basic JSON configuration file without modifying the filesystem."""

    path = Path(file_path)
    try:
        with path.open("r", encoding="utf-8") as config_file:
            config = json.load(config_file)
    except FileNotFoundError as exc:
        raise ValueError(f"configuration file not found: {path}") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"could not read configuration file {path}: {exc}") from exc
    if not isinstance(config, dict):
        raise ValueError("configuration file must contain a JSON object")
    return config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Price a European option with Black-Scholes")
    parser.add_argument("--config", type=Path, help="Optional read-only JSON input file")
    parser.add_argument("--spot", type=float)
    parser.add_argument("--strike", type=float)
    parser.add_argument("--time", type=float, help="Years to expiry")
    parser.add_argument("--volatility", type=float, help="Decimal volatility")
    parser.add_argument("--rate", type=float, help="Decimal risk-free rate")
    parser.add_argument("--dividend", type=float, help="Decimal dividend yield")
    parser.add_argument("--type", choices=("call", "put"))
    parser.add_argument("--heatmap", action="store_true", help="Display a Seaborn heatmap")
    parser.add_argument("--curves", action="store_true", help="Display Seaborn price curves")
    parser.add_argument("--spot-min", type=float)
    parser.add_argument("--spot-max", type=float)
    parser.add_argument("--vol-min", type=float, default=0.05)
    parser.add_argument("--vol-max", type=float, default=0.60)
    parser.add_argument("--points", type=int, default=10)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        config = load_json_config(args.config) if args.config else {}
    except ValueError as exc:
        parser.error(str(exc))

    def setting(name: str, default: Any = None) -> Any:
        command_line_value = getattr(args, name)
        return command_line_value if command_line_value is not None else config.get(name, default)

    spot = setting("spot")
    strike = setting("strike")
    time_to_expiry = setting("time")
    volatility = setting("volatility")
    missing = [
        name
        for name, value in (
            ("spot", spot),
            ("strike", strike),
            ("time", time_to_expiry),
            ("volatility", volatility),
        )
        if value is None
    ]
    if missing:
        parser.error("missing required values: " + ", ".join(f"--{name}" for name in missing))

    rate = setting("rate", 0.0)
    dividend = setting("dividend", 0.0)
    option_type = setting("type", "call")
    result = black_scholes(
        spot,
        strike,
        time_to_expiry,
        volatility,
        rate,
        option_type,
        dividend,
    )
    print(json.dumps(result.as_dict(), indent=2))
    if args.heatmap or args.curves:
        spot_min = args.spot_min if args.spot_min is not None else spot * 0.7
        spot_max = args.spot_max if args.spot_max is not None else spot * 1.3
        spots = _range(spot_min, spot_max, args.points)
        vols = _range(args.vol_min, args.vol_max, args.points)
    if args.heatmap:
        plot_price_heatmap(
            spots,
            vols,
            strike=strike,
            time_to_expiry=time_to_expiry,
            risk_free_rate=rate,
            dividend_yield=dividend,
            option_type=option_type,
            show=not args.curves,
        )
    if args.curves:
        plot_price_curves(
            spots,
            vols,
            strike=strike,
            time_to_expiry=time_to_expiry,
            risk_free_rate=rate,
            dividend_yield=dividend,
            option_type=option_type,
        )


if __name__ == "__main__":
    main()
